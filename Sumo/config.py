# =============================================================================
#  config.py  –  Parámetros de configuración del robot sumo
#  Ajusta estos valores según tu hardware y entorno de competición
# =============================================================================

# ── Puerto serie ──────────────────────────────────────────────────────────────
LIDAR_PORT   = "/dev/ttyUSB0"   # Puerto del YDLidar en la Raspberry Pi
ARDUINO_PORT = "/dev/ttyACM0"   # Puerto del Arduino (pymata4 lo detecta solo)
CAMERA_INDEX = 0                 # Índice de la webcam (0 = primera cámara USB)

# ── Ángulos excluidos del LiDAR (barras propias del robot) ───────────────────
# Cada tupla es un rango (inicio, fin) en grados que se ignora en el escaneo.
# El LiDAR mide 0-360°; ajusta estos rangos girando manualmente el robot y
# viendo qué ángulos corresponden a cada barra en el software de diagnóstico.
# Ejemplo: barra delantera izquierda entre 10° y 30°, etc.
OWN_BARS_ANGLE_EXCLUSIONS = [
    (350, 360), (0, 15),   # Barra delantera (cruza el 0°)
    (80,  100),            # Barra lateral derecha
    (170, 190),            # Barra trasera
    (260, 280),            # Barra lateral izquierda
]

# ── LiDAR – umbrales de detección ────────────────────────────────────────────
LIDAR_MIN_DIST_MM     = 50     # Distancia mínima válida (filtra ruido)
LIDAR_MAX_DIST_MM     = 1500   # Distancia máxima de detección de rival
LIDAR_ATTACK_DIST_MM  = 350    # Distancia a la que se pasa a modo ATAQUE

# ── Velocidades ───────────────────────────────────────────────────────────────
VEL_BUSQUEDA  = 160   # Velocidad de giro durante búsqueda
VEL_SEGUIR    = 200   # Velocidad avanzando hacia el rival
VEL_ATAQUE    = 255   # Velocidad máxima en ataque
VEL_EVASION   = 220   # Velocidad al retroceder de la línea

# ── Cámara – detección de línea (borde de la lona) ───────────────────────────
# La lona es BLANCA; el borde exterior de la lona sumo estándar es NEGRO.
# Si tu lona es diferente, ajusta los valores HSV o el método de umbralización.
LINE_DETECTION_METHOD = "dark"  # "dark"  → detecta borde oscuro en lona clara
                                 # "light" → detecta borde claro en lona oscura

# Umbral de brillo para detectar el borde negro (0-255)
LINE_DARK_THRESHOLD  = 60     # Píxeles más oscuros que esto = línea/borde
LINE_LIGHT_THRESHOLD = 200    # Píxeles más brillantes que esto = línea blanca

# Porcentaje mínimo de píxeles de borde en la ROI para activar evasión
LINE_PIXEL_RATIO = 0.12        # 12 % de la ROI → "línea detectada"

# Altura de la franja inferior de la imagen que se analiza como zona de línea
LINE_ROI_HEIGHT = 80           # píxeles desde abajo de la imagen

# ── Cámara – detección de rival ───────────────────────────────────────────────
# El rival es blanco igual que la lona → usamos detección de CONTORNOS/MOVIMIENTO
# y validamos con el LiDAR para reducir falsos positivos.
RIVAL_MIN_AREA   = 200    # Área mínima del contorno rival (px²)
RIVAL_MAX_AREA   = 8000   # Área máxima (descarta objetos grandes = fondo)
RIVAL_CENTER_MARGIN = 80  # Margen en px alrededor del centro → "centrado"

# ── Máquina de estados – tiempos ──────────────────────────────────────────────
SEARCH_TURN_DURATION  = 0.25   # Segundos girando en cada paso de búsqueda
EVADE_BACK_DURATION   = 0.35   # Segundos retrocediendo al detectar línea
EVADE_TURN_DURATION   = 0.30   # Segundos girando tras retroceder
LOOP_SLEEP            = 0.03   # Período del bucle principal (≈33 Hz)
