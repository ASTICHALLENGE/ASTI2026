"""
Opcion7_Python313.py  —  Robot tira-bolos con detección por Ultralytics YOLOv8
═══════════════════════════════════════════════════════════════════════════════

Compatible con Python 3.13.5 usando Ultralytics YOLO (inferencia local).

CONFIGURACIÓN INICIAL:
══════════════════════════════════════════════════════════════════════════════
1. Instalar dependencias compatibles con Python 3.13.5:
   pip install ultralytics opencv-contrib-python

2. Exportar el modelo desde Roboflow a formato YOLOv8:
   - Ve a tu proyecto en Roboflow: https://app.roboflow.com/
   - Workspace: lsc-kik8c
   - Proyecto: bowling-pin-detection
   - Versión: 3
   - Click en "Export" → Selecciona "YOLOv8" como formato
   - Descarga el archivo .zip
   - Extrae el contenido y busca el archivo "best.pt" o "weights/best.pt"

3. Colocar el modelo:
   - Crea la carpeta: TiraBolos/models/
   - Copia el archivo .pt a: TiraBolos/models/bowling_pin_yolov8.pt
   
   Estructura esperada:
   ASTI2026/
   ├── TiraBolos/
   │   ├── models/
   │   │   └── bowling_pin_yolov8.pt  ← Archivo del modelo
   │   └── Opcion7_Python313.py       ← Este archivo

LÓGICA DE MOVIMIENTO:
══════════════════════════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────────────────────┐
│  Sin bolos detectados  → BUSCAR (giro lento después de 15 frames)      │
│  Bolo a la izquierda   → IZQUIERDA (gira hacia el bolo)                │
│  Bolo a la derecha     → DERECHA (gira hacia el bolo)                  │
│  Bolo centrado + lejos → AVANZA (velocidad normal)                     │
│  Bolo centrado + cerca → SPRINT (velocidad máxima, área >= 8000 px²)  │
└─────────────────────────────────────────────────────────────────────────┘

DIFERENCIAS CON OPCION5.PY:
══════════════════════════════════════════════════════════════════════════════
- Usa Ultralytics YOLO en lugar de InferenceHTTPClient (Roboflow API)
- Inferencia local (no requiere conexión a internet ni API key)
- Formato de resultados diferente (Ultralytics vs Roboflow)
- Compatible con Python 3.13.5
"""

import time
import cv2
import sys
import os
from pathlib import Path

# Importar Ultralytics YOLO
try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: No se encuentra el módulo 'ultralytics'")
    print("Instala con: pip install ultralytics")
    sys.exit(1)

# Importar módulo de movimiento personalizado
sys.path.append('/home/asti/CodigosRobot')
import Movimiento as mov

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DEL MODELO
# ══════════════════════════════════════════════════════════════════════════════
# Ruta al modelo YOLOv8 exportado desde Roboflow
# Ajusta esta ruta según donde hayas colocado tu archivo .pt
MODEL_PATH = "TiraBolos/models/bowling_pin_yolov8.pt"

# Verificar que el modelo existe
if not os.path.exists(MODEL_PATH):
    print("═" * 80)
    print("ERROR: No se encuentra el archivo del modelo")
    print(f"Ruta buscada: {os.path.abspath(MODEL_PATH)}")
    print()
    print("SOLUCIÓN:")
    print("1. Exporta tu modelo desde Roboflow en formato YOLOv8")
    print("2. Descarga el archivo .pt (best.pt o similar)")
    print("3. Colócalo en: TiraBolos/models/bowling_pin_yolov8.pt")
    print()
    print("Alternativamente, modifica MODEL_PATH en este archivo")
    print("para apuntar a la ubicación correcta de tu modelo.")
    print("═" * 80)
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DEL ROBOT — ajusta estos valores según tu robot
# ══════════════════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════════════════
#  INICIALIZACIÓN
# ══════════════════════════════════════════════════════════════════════════════
print("Cargando modelo YOLOv8...")
try:
    # Cargar el modelo YOLO
    # verbose=False evita mensajes excesivos durante la inferencia
    model = YOLO(MODEL_PATH)
    print(f"✓ Modelo cargado: {MODEL_PATH}")
except Exception as e:
    print(f"ERROR al cargar el modelo: {e}")
    sys.exit(1)

# Inicializar cámara
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error al conectar la cámara")
    sys.exit()

# Configurar velocidad inicial del robot
mov.setVelocidad(VEL_NORMAL)

# ══════════════════════════════════════════════════════════════════════════════
#  ESTADO DEL ROBOT
# ══════════════════════════════════════════════════════════════════════════════
frames_sin_bolo  = 0
dir_busqueda     = 1      # +1 = gira derecha, -1 = gira izquierda
accion_anterior  = ""

# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════
def elegir_mejor_bolo(results):
    """
    De todas las detecciones de YOLO, devuelve la que tenga mayor área
    (= el bolo más grande / más cercano).
    Filtra por confianza mínima.
    
    Args:
        results: Objeto Results de Ultralytics YOLO
        
    Returns:
        tuple: (mejor_deteccion_dict, area_maxima)
               mejor_deteccion_dict contiene: {x, y, w, h, conf}
               Si no hay detecciones válidas, retorna (None, 0)
    """
    mejor      = None
    mayor_area = 0
    
    # Extraer las cajas detectadas (boxes)
    # results[0] porque model() retorna una lista con un elemento por imagen
    if len(results) == 0 or results[0].boxes is None:
        return None, 0
    
    boxes = results[0].boxes
    
    # Iterar sobre cada detección
    for box in boxes:
        # Obtener confianza
        conf = float(box.conf[0])
        if conf < CONF_MIN:
            continue
        
        # Obtener coordenadas del bounding box en formato xyxy
        # xyxy = [x1, y1, x2, y2] (esquina superior izquierda y esquina inferior derecha)
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, xyxy)
        
        # Calcular centro y dimensiones
        w = x2 - x1
        h = y2 - y1
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        area = w * h
        
        # Seleccionar el bolo con mayor área
        if area > mayor_area:
            mayor_area = area
            mejor = {
                'x': cx,      # centro X
                'y': cy,      # centro Y
                'w': w,       # ancho
                'h': h,       # alto
                'x1': x1,     # esquina superior izquierda X
                'y1': y1,     # esquina superior izquierda Y
                'x2': x2,     # esquina inferior derecha X
                'y2': y2,     # esquina inferior derecha Y
                'conf': conf  # confianza
            }
    
    return mejor, mayor_area


def aplicar_movimiento(accion, vel):
    """
    Aplica el movimiento solo si ha cambiado (evita spam al Arduino).
    
    Args:
        accion: String con la acción ("AVANZA", "IZQUIERDA", "DERECHA", "STOP")
        vel: Velocidad a aplicar
    """
    global accion_anterior
    if accion == accion_anterior:
        return
    mov.setVelocidad(vel)
    if   accion == "AVANZA":     mov.Avanza()
    elif accion == "IZQUIERDA":  mov.Izquierda()
    elif accion == "DERECHA":    mov.Derecha()
    elif accion == "STOP":       mov.Stop()
    accion_anterior = accion


# ══════════════════════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
print("TiraBolos v7 — Ultralytics YOLOv8 (Python 3.13.5). Pulsa 'q' para salir.")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error al capturar frame")
        break

    t0 = time.time()

    # ── 1. INFERENCIA CON YOLO ────────────────────────────────────────────────
    try:
        # Ejecutar detección
        # conf: umbral de confianza mínimo
        # verbose: False para evitar mensajes en consola
        # stream: False para procesar una sola imagen
        results = model(frame, conf=CONF_MIN, verbose=False)
        
    except Exception as e:
        print(f"\n[ERROR YOLO] {e}")
        aplicar_movimiento("STOP", VEL_NORMAL)
        results = []

    # Calcular FPS
    fps = 1.0 / max(time.time() - t0, 1e-6)

    # ── 2. ELEGIR OBJETIVO (BOLO MÁS CERCANO) ─────────────────────────────────
    bolo, area = elegir_mejor_bolo(results)

    # ── 3. DECISIÓN DE MOVIMIENTO ─────────────────────────────────────────────
    if bolo:
        # Bolo detectado: resetear contador
        frames_sin_bolo = 0

        cx = bolo['x']   # centro X del bounding box
        cy = bolo['y']   # centro Y del bounding box

        if area >= AREA_CERCA:
            # ── Bolo cerca: SPRINT ────────────────────────────────────────────
            accion = "AVANZA"
            vel    = VEL_ATAQUE
            label  = f"SPRINT  area={int(area)}"

        elif cx < ZONA_IZQ:
            # ── Bolo a la izquierda ───────────────────────────────────────────
            accion       = "IZQUIERDA"
            vel          = VEL_NORMAL
            dir_busqueda = -1
            label  = f"IZQ  cx={cx}"

        elif cx > ZONA_DER:
            # ── Bolo a la derecha ─────────────────────────────────────────────
            accion       = "DERECHA"
            vel          = VEL_NORMAL
            dir_busqueda = 1
            label  = f"DER  cx={cx}"

        else:
            # ── Bolo centrado: AVANZA ─────────────────────────────────────────
            accion = "AVANZA"
            vel    = VEL_NORMAL
            label  = f"AVANZA  cx={cx}"

        # Aplicar el movimiento decidido
        aplicar_movimiento(accion, vel)

        # ── Dibujar detección en el frame ─────────────────────────────────────
        if DEBUG:
            x1, y1 = bolo['x1'], bolo['y1']
            x2, y2 = bolo['x2'], bolo['y2']
            conf   = bolo['conf']
            
            # Dibujar rectángulo verde alrededor del bolo
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            # Dibujar punto rojo en el centro
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            # Mostrar confianza y acción
            cv2.putText(frame, f"{conf:.0%}  {label}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)

    else:
        # ── Sin bolos detectados ──────────────────────────────────────────────
        frames_sin_bolo += 1

        if frames_sin_bolo >= MAX_SIN_BOLO:
            # Activar modo búsqueda: girar despacio
            mov.setVelocidad(VEL_BUSQUEDA)
            if dir_busqueda > 0:
                mov.Derecha()
            else:
                mov.Izquierda()
            accion_anterior = "BUSQUEDA"
            label = f"BUSQUEDA (sin bolo {frames_sin_bolo}f)"
        else:
            # Esperar un poco antes de buscar
            aplicar_movimiento("STOP", VEL_NORMAL)
            label = "ESPERA"

        if DEBUG:
            cv2.putText(frame, label, (8, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)

    # ── 4. VISUALIZACIÓN DEBUG ────────────────────────────────────────────────
    if DEBUG:
        # Dibujar líneas de zonas (izquierda, centro, derecha)
        cv2.line(frame, (ZONA_IZQ, 0), (ZONA_IZQ, 480), (200, 100, 0), 1)
        cv2.line(frame, (ZONA_DER, 0), (ZONA_DER, 480), (200, 100, 0), 1)
        cv2.line(frame, (CENTRO_X, 0), (CENTRO_X, 480), (100, 100, 100), 1)

        # HUD: mostrar FPS, número de bolos detectados y acción actual
        if len(results) > 0 and results[0].boxes is not None:
            n_bolos = len([b for b in results[0].boxes if float(b.conf[0]) >= CONF_MIN])
        else:
            n_bolos = 0
            
        cv2.putText(frame, f"FPS:{fps:.1f}  Bolos:{n_bolos}  {accion_anterior}",
                    (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 255, 0) if "AVANZA" in accion_anterior or "SPRINT" in accion_anterior
                    else (0, 140, 255), 2)

        # Mostrar ventana con el frame procesado
        cv2.imshow("TiraBolos — Ultralytics YOLOv8", frame)

    # Salir si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ══════════════════════════════════════════════════════════════════════════════
#  LIMPIEZA AL SALIR
# ══════════════════════════════════════════════════════════════════════════════
print("\nCerrando...")
cam.release()
cv2.destroyAllWindows()
mov.Stop()
mov.setVelocidad(0)
print("✓ Programa finalizado correctamente")

# Made with Bob
