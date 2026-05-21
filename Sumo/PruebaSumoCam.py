"""
intento2Sumo.py  —  Sumo con corrección lateral por cámara
══════════════════════════════════════════════════════════════

Igual que intento1Sumo.py pero añade un hilo de cámara que detecta
las ruedas negras del rival y aplica pequeñas correcciones laterales
cuando el robot avanza hacia él.

  Sensor US → sabe QUÉ LADO tiene al rival
  Cámara    → sabe si está MÁS A LA IZQUIERDA O DERECHA dentro de ese lado

Detección:
  El rival es blanco con ruedas negras → buscamos blobs oscuros.
  El borde del tatami también es negro, así que filtramos los
  contornos que aparecen demasiado cerca de los bordes del frame.
"""

import threading
import time
import cv2
import numpy as np
from pymata4 import pymata4
import sys

sys.path.append('/home/asti/CodigosRobot')
import Omni

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
DEBUG = True

# ── Sensores ─────────────────────────────────────────────────
DIST_RIVAL   = 20     # cm — distancia para considerar rival detectado

trig1, echo1 = 22, 23   # Adelante
trig2, echo2 = 24, 25   # Derecha
trig3, echo3 = 26, 27   # Izquierda
trig4, echo4 = 28, 29   # Atras

ir1, ir2, ir3, ir4 = 30, 31, 32, 33

BLANCO = 0
NEGRO  = 1

# ── Cámara ───────────────────────────────────────────────────
# ROI vertical: excluye el techo (filas 0‒110) y el suelo cercano
# donde el borde negro del tatami aparece con más fuerza (filas 380‒480)
CAM_ROI_Y1 = 110
CAM_ROI_Y2 = 370

# Margen horizontal: ignora contornos con centroide muy cerca del borde
# del frame (probablemente el borde del tatami, no ruedas del rival)
CAM_MARGEN_X = 90     # px desde cada lado que se descarta

# Umbral de oscuridad: 0‒255; las ruedas negras están cerca de 0,
# el tatami blanco cerca de 255. Ajusta si hay falsos positivos.
CAM_THRESH   = 60

# Área mínima de un contorno para ser considerado rueda
CAM_AREA_MIN = 450

# Zona muerta: el rival debe estar > N px fuera del centro para corregir
CAM_ZONA_MUERTA = 80

# Centro horizontal del frame
CAM_CENTRO = 320

# ══════════════════════════════════════════════════════════════
#  HARDWARE
# ══════════════════════════════════════════════════════════════
board = pymata4.Pymata4()

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error: cámara no disponible.")
    board.shutdown()
    sys.exit()

# ══════════════════════════════════════════════════════════════
#  ESTADO COMPARTIDO
# ══════════════════════════════════════════════════════════════
distAct  = {"Adelante": 0, "Derecha": 0, "Izquierda": 0, "Atras": 0}
colorAct = {"Adelante": BLANCO, "Derecha": BLANCO,
            "Izquierda": BLANCO, "Atras": BLANCO}

# Variables de cámara (el hilo las escribe, el bucle principal las lee)
cam_error   = 0      # offset del rival respecto al centro: negativo=izq, positivo=der
cam_visible = False  # True si se detecta al rival en cámara
cam_lock    = threading.Lock()

busqueda = 0

# ══════════════════════════════════════════════════════════════
#  CALLBACKS DE SENSORES
# ══════════════════════════════════════════════════════════════
nombres_US = {trig1: "Adelante", trig2: "Derecha",
              trig3: "Izquierda", trig4: "Atras"}
nombres_IR = {ir1: "Adelante", ir2: "Derecha",
              ir3: "Izquierda", ir4: "Atras"}

def leerUS(data):
    nombre = nombres_US.get(data[1])
    if nombre:
        distAct[nombre] = data[2]

def leerIR(data):
    nombre = nombres_IR.get(data[1])
    if nombre:
        colorAct[nombre] = data[2]

# ══════════════════════════════════════════════════════════════
#  HILO DE CÁMARA
# ══════════════════════════════════════════════════════════════
def hilo_camara():
    """
    Detecta las ruedas negras del rival en el ROI central.
    Pasos:
      1. Recortar ROI vertical para reducir el borde del tatami
      2. Umbral oscuro → píxeles de las ruedas se vuelven blancos
      3. Eliminar contornos con centroide muy pegado al borde del frame
      4. El contorno más grande restante = rival → cam_error = su X − 320
    """
    global cam_error, cam_visible

    roi_h = CAM_ROI_Y2 - CAM_ROI_Y1   # alto del ROI en píxeles

    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        roi = frame[CAM_ROI_Y1:CAM_ROI_Y2, 0:640]

        # ── Preprocesado ────────────────────────────────────────
        gray  = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur  = cv2.GaussianBlur(gray, (5, 5), 0)
        _, th = cv2.threshold(blur, CAM_THRESH, 255, cv2.THRESH_BINARY_INV)

        k  = np.ones((3, 3), np.uint8)
        th = cv2.morphologyEx(th, cv2.MORPH_OPEN,  k)
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, k)

        # ── Filtrado de contornos ────────────────────────────────
        contornos, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidatos = []
        for c in contornos:
            if cv2.contourArea(c) < CAM_AREA_MIN:
                continue
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Descartar si el centroide está demasiado cerca del borde lateral
            # (señal de que es el borde del tatami, no el rival)
            if cx < CAM_MARGEN_X or cx > (640 - CAM_MARGEN_X):
                continue

            candidatos.append((cv2.contourArea(c), cx, cy, c))

        # ── Actualizar estado compartido ─────────────────────────
        if candidatos:
            # Mayor área → más probable que sean las ruedas del rival
            candidatos.sort(reverse=True)
            _, cx_rival, cy_rival, cont_rival = candidatos[0]
            error = cx_rival - CAM_CENTRO

            with cam_lock:
                cam_error   = error
                cam_visible = True

            # ── Visualización debug ──────────────────────────────
            if DEBUG:
                cv2.drawContours(roi, [cont_rival], -1, (0, 165, 255), 2)
                cv2.circle(roi, (cx_rival, cy_rival), 8, (0, 255, 0), -1)
                cv2.line(roi, (CAM_CENTRO, 0), (CAM_CENTRO, roi_h), (200, 80, 0), 1)
                # Líneas de zona muerta
                cv2.line(roi, (CAM_CENTRO - CAM_ZONA_MUERTA, 0),
                              (CAM_CENTRO - CAM_ZONA_MUERTA, roi_h), (80, 80, 255), 1)
                cv2.line(roi, (CAM_CENTRO + CAM_ZONA_MUERTA, 0),
                              (CAM_CENTRO + CAM_ZONA_MUERTA, roi_h), (80, 80, 255), 1)
                color_txt = (0, 255, 0) if abs(error) <= CAM_ZONA_MUERTA else (0, 80, 255)
                cv2.putText(roi, f"Rival: {error:+d}px", (8, 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_txt, 2)
        else:
            with cam_lock:
                cam_error   = 0
                cam_visible = False

            if DEBUG:
                cv2.putText(roi, "Sin rival", (8, 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (60, 60, 200), 2)

        if DEBUG:
            cv2.imshow("Camara Sumo", roi)
            cv2.waitKey(1)

# ══════════════════════════════════════════════════════════════
#  MOVIMIENTO CON CORRECCIÓN DE CÁMARA
# ══════════════════════════════════════════════════════════════
def avanzar_con_correccion():
    """
    Avanza hacia el frente aplicando corrección lateral de cámara.

    Lógica:
      - Rival centrado (o no visible)  → Avanza recto
      - Rival a la derecha del centro  → AvanzaDer  (sesga hacia él)
      - Rival a la izquierda del centro → AvanzaIzq
    """
    with cam_lock:
        err   = cam_error
        visto = cam_visible

    if not visto or abs(err) <= CAM_ZONA_MUERTA:
        Omni.Avanza()
        if DEBUG:
            label = "RECTO" if visto else "RECTO (sin vision)"
    elif err > 0:
        Omni.AvanzaDer()
        if DEBUG:
            label = f"CORRECCION +DER  ({err:+d}px)"
    else:
        Omni.AvanzaIzq()
        if DEBUG:
            label = f"CORRECCION +IZQ  ({err:+d}px)"

    if DEBUG:
        print(f"[ATAQUE] {label:<35}", end='\r')

# ══════════════════════════════════════════════════════════════
#  INICIALIZACIÓN DE SENSORES
# ══════════════════════════════════════════════════════════════
print("Inicializando sensores...")
board.set_pin_mode_sonar(trig1, echo1, leerUS)
board.set_pin_mode_sonar(trig2, echo2, leerUS)
board.set_pin_mode_sonar(trig3, echo3, leerUS)
board.set_pin_mode_sonar(trig4, echo4, leerUS)

board.set_pin_mode_digital_input(ir1, callback=leerIR)
board.set_pin_mode_digital_input(ir2, callback=leerIR)
board.set_pin_mode_digital_input(ir3, callback=leerIR)
board.set_pin_mode_digital_input(ir4, callback=leerIR)
time.sleep(0.5)

# ── Arrancar hilo de cámara ───────────────────────────────────
t_cam = threading.Thread(target=hilo_camara, daemon=True)
t_cam.start()
print("Hilo de cámara iniciado.")

# ── Giro inicial de búsqueda ──────────────────────────────────
Omni.setVelocidad(160)
Omni.GiroDer()
time.sleep(1)
Omni.setVelocidad(130)

# ══════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════
print("Sumo v2 — cámara activa. Ctrl+C para detener.")

try:
    while True:
        col  = colorAct.copy()
        dist = distAct.copy()

        # ── EVASIÓN (prioridad absoluta: borde detectado) ─────
        if any(v == NEGRO for v in col.values()):
            if   col["Adelante"]  == NEGRO:
                if   col["Derecha"]   == NEGRO: Omni.AtrasIzq()
                elif col["Izquierda"] == NEGRO: Omni.AtrasDer()
                else:                            Omni.Atras()
            elif col["Atras"] == NEGRO:
                if   col["Derecha"]   == NEGRO: Omni.AvanzaIzq()
                elif col["Izquierda"] == NEGRO: Omni.AvanzaDer()
                else:                            Omni.Avanza()
            elif col["Derecha"]   == NEGRO:     Omni.Izquierda()
            elif col["Izquierda"] == NEGRO:     Omni.Derecha()
            busqueda += 1
            if DEBUG:
                print(f"[EVASION]  {col}                  ", end='\r')

        # ── SEGUIMIENTO / ATAQUE (rival detectado por US) ─────
        # Solo se aplica corrección de cámara cuando el rival está
        # delante. En los otros lados giramos directamente.
        elif dist["Adelante"] > 0 and dist["Adelante"] < DIST_RIVAL:
            avanzar_con_correccion()   # ← corrección de cámara aquí
            busqueda = 0

        elif dist["Derecha"] > 0 and dist["Derecha"] < DIST_RIVAL:
            Omni.Derecha()
            busqueda = 0
            if DEBUG:
                print("[US] Rival a la derecha               ", end='\r')

        elif dist["Izquierda"] > 0 and dist["Izquierda"] < DIST_RIVAL:
            Omni.Izquierda()
            busqueda = 0
            if DEBUG:
                print("[US] Rival a la izquierda             ", end='\r')

        elif dist["Atras"] > 0 and dist["Atras"] < DIST_RIVAL:
            Omni.Atras()
            busqueda = 0
            if DEBUG:
                print("[US] Rival detrás                     ", end='\r')

        # ── BÚSQUEDA (sin rival en ningún lado) ───────────────
        else:
            if   busqueda > 30:
                Omni.AtrasIzq()
                busqueda += 1
                if busqueda > 40:
                    busqueda = 0
            elif busqueda > 20:
                Omni.AtrasDer()
                busqueda += 1
            elif busqueda > 10:
                Omni.AvanzaDer()
                busqueda += 1
            else:
                Omni.AvanzaIzq()
                busqueda += 1
            if DEBUG:
                print(f"[BUSQUEDA] paso={busqueda:<3}                   ", end='\r')

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nDeteniendo...")
finally:
    cam.release()
    cv2.destroyAllWindows()
    Omni.Stop()
    board.shutdown()