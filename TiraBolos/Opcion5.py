"""
Opcion5Roboflow.py  —  Robot tira-bolos con detección por Roboflow
══════════════════════════════════════════════════════════════════════

Usa el modelo público de Roboflow:
  workspace : lsc-kik8c
  model_id  : bowling-pin-detection/3

Lógica de movimiento (igual que Opcion3YOLO.py pero mejorada):
  ┌─────────────────────────────────────────────────────────────┐
  │  Sin bolos detectados  → BUSCAR (giro lento)                │
  │  Bolo a la izquierda   → IZQUIERDA                          │
  │  Bolo a la derecha     → DERECHA                            │
  │  Bolo centrado + lejos → AVANZA                             │
  │  Bolo centrado + cerca → ATAQUE (velocidad máxima)          │
  └─────────────────────────────────────────────────────────────┘

Instalar dependencias (si no las tienes):
  pip install inference-sdk opencv-contrib-python
"""

import time
import cv2
import sys
from inference_sdk import InferenceHTTPClient

sys.path.append('/home/asti/CodigosRobot')
import Movimiento as mov

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN  — ajusta estos valores según tu robot
# ══════════════════════════════════════════════════════════════
API_KEY       = ""          # ← Pega aquí tu API Key de Roboflow
MODEL_ID      = "bowling-pin-detection/3"
API_URL       = "https://serverless.roboflow.com"

# Velocidades
VEL_NORMAL    = 130         # navegación suave
VEL_ATAQUE    = 180         # sprint final hacia el bolo
VEL_BUSQUEDA  = 110         # giro lento buscando

# Zonas horizontales del frame (640 px de ancho)
ZONA_IZQ      = 220         # px — todo lo que esté < ZONA_IZQ es "izquierda"
ZONA_DER      = 420         # px — todo lo que esté > ZONA_DER es "derecha"
CENTRO_X      = 320         # centro del frame

# Umbral de tamaño (bbox_area) para considerar que el bolo está "cerca"
# y lanzar el sprint. Ajusta según la altura de la cámara.
AREA_CERCA    = 8000        # px²  (ancho*alto de la caja detectada)

# Confianza mínima para aceptar una detección
CONF_MIN      = 0.40

# Máximo de frames sin detección antes de activar modo búsqueda
MAX_SIN_BOLO  = 15

DEBUG         = True

# ══════════════════════════════════════════════════════════════
#  INICIALIZACIÓN
# ══════════════════════════════════════════════════════════════
client = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error al conectar la cámara")
    sys.exit()

mov.setVelocidad(VEL_NORMAL)

# ══════════════════════════════════════════════════════════════
#  ESTADO
# ══════════════════════════════════════════════════════════════
frames_sin_bolo  = 0
dir_busqueda     = 1      # +1 = gira derecha, -1 = gira izquierda
accion_anterior  = ""

# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════
def elegir_mejor_bolo(predicciones):
    """
    De todas las detecciones, devuelve la que tenga mayor área
    (= el bolo más grande / más cercano).
    Filtra por confianza mínima.
    """
    mejor      = None
    mayor_area = 0

    for p in predicciones:
        if p.get("confidence", 0) < CONF_MIN:
            continue
        area = p.get("width", 0) * p.get("height", 0)
        if area > mayor_area:
            mayor_area = area
            mejor = p

    return mejor, mayor_area


def aplicar_movimiento(accion, vel):
    """Aplica el movimiento solo si ha cambiado (evita spam al Arduino)."""
    global accion_anterior
    if accion == accion_anterior:
        return
    mov.setVelocidad(vel)
    if   accion == "AVANZA":     mov.Avanza()
    elif accion == "IZQUIERDA":  mov.Izquierda()
    elif accion == "DERECHA":    mov.Derecha()
    elif accion == "STOP":       mov.Stop()
    accion_anterior = accion


# ══════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════
print("TiraBolos v5 — Roboflow. Pulsa 'q' para salir.")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error al capturar frame")
        break

    t0 = time.time()

    # ── 1. Inferencia ──────────────────────────────────────────
    try:
        result       = client.infer(frame, model_id=MODEL_ID)
        predicciones = result.get("predictions", [])
    except Exception as e:
        print(f"\n[ERROR Roboflow] {e}")
        aplicar_movimiento("STOP", VEL_NORMAL)
        predicciones = []

    fps = 1.0 / max(time.time() - t0, 1e-6)

    # ── 2. Elegir objetivo ─────────────────────────────────────
    bolo, area = elegir_mejor_bolo(predicciones)

    # ── 3. Decisión de movimiento ──────────────────────────────
    if bolo:
        frames_sin_bolo = 0

        cx = int(bolo["x"])   # centro X del bounding box
        cy = int(bolo["y"])   # centro Y del bounding box

        if area >= AREA_CERCA:
            # ── Bolo cerca: sprint ────────────────────────────
            accion = "AVANZA"
            vel    = VEL_ATAQUE
            label  = f"SPRINT  area={int(area)}"

        elif cx < ZONA_IZQ:
            # ── Bolo a la izquierda ───────────────────────────
            accion       = "IZQUIERDA"
            vel          = VEL_NORMAL
            dir_busqueda = -1
            label  = f"IZQ  cx={cx}"

        elif cx > ZONA_DER:
            # ── Bolo a la derecha ─────────────────────────────
            accion       = "DERECHA"
            vel          = VEL_NORMAL
            dir_busqueda = 1
            label  = f"DER  cx={cx}"

        else:
            # ── Bolo centrado: avanza ─────────────────────────
            accion = "AVANZA"
            vel    = VEL_NORMAL
            label  = f"AVANZA  cx={cx}"

        aplicar_movimiento(accion, vel)

        # ── Dibujar detección ──────────────────────────────────
        if DEBUG:
            w, h   = int(bolo["width"]), int(bolo["height"])
            x1, y1 = cx - w // 2, cy - h // 2
            x2, y2 = cx + w // 2, cy + h // 2
            conf   = bolo.get("confidence", 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"{conf:.0%}  {label}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)

    else:
        # ── Sin bolos detectados ───────────────────────────────
        frames_sin_bolo += 1

        if frames_sin_bolo >= MAX_SIN_BOLO:
            # Girar despacio para buscar
            mov.setVelocidad(VEL_BUSQUEDA)
            if dir_busqueda > 0:
                mov.Derecha()
            else:
                mov.Izquierda()
            accion_anterior = "BUSQUEDA"
            label = f"BUSQUEDA (sin bolo {frames_sin_bolo}f)"
        else:
            aplicar_movimiento("STOP", VEL_NORMAL)
            label = "ESPERA"

        if DEBUG:
            cv2.putText(frame, label, (8, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)

    # ── 4. Visualización ───────────────────────────────────────
    if DEBUG:
        # Líneas de zonas
        cv2.line(frame, (ZONA_IZQ, 0), (ZONA_IZQ, 480), (200, 100, 0), 1)
        cv2.line(frame, (ZONA_DER, 0), (ZONA_DER, 480), (200, 100, 0), 1)
        cv2.line(frame, (CENTRO_X, 0), (CENTRO_X, 480), (100, 100, 100), 1)

        # HUD
        n_bolos = len([p for p in predicciones if p.get("confidence", 0) >= CONF_MIN])
        cv2.putText(frame, f"FPS:{fps:.1f}  Bolos:{n_bolos}  {accion_anterior}",
                    (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 255, 0) if "AVANZA" in accion_anterior or "SPRINT" in accion_anterior
                    else (0, 140, 255), 2)

        cv2.imshow("TiraBolos — Roboflow", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ══════════════════════════════════════════════════════════════
#  LIMPIEZA
# ══════════════════════════════════════════════════════════════
print("\nCerrando...")
cam.release()
cv2.destroyAllWindows()
mov.Stop()
mov.setVelocidad(0)