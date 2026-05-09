# =============================================================================
#  sumo_main.py  –  Máquina de estados principal del robot sumo
#
#  Estados:
#   BUSQUEDA  → Girar buscando rival con LiDAR
#   ORIENTAR  → Rival detectado, girar hacia él (cámara + LiDAR)
#   SEGUIR    → Avanzar hacia el rival
#   ATAQUE    → Rival muy cerca, máxima velocidad
#   EVASION   → Línea de borde detectada, retroceder y girar
#
#  Prioridades (de mayor a menor):
#   1. Evasión de borde  ← siempre tiene prioridad absoluta
#   2. LiDAR detecta rival → ORIENTAR / SEGUIR / ATAQUE
#   3. Cámara detecta rival → corrección fina de dirección
#   4. Sin información → BUSQUEDA
# =============================================================================

import time
import signal
import sys

sys.path.append('/home/asti/CodigosRobot')
import Movimiento as mot
from lidar_module  import LidarScanner
from vision_module import VisionSystem
from config import (
    VEL_BUSQUEDA, VEL_SEGUIR, VEL_ATAQUE, VEL_EVASION,
    LIDAR_ATTACK_DIST_MM,
    SEARCH_TURN_DURATION, EVADE_BACK_DURATION, EVADE_TURN_DURATION,
    LOOP_SLEEP,
    RIVAL_CENTER_MARGIN,
)

# ── Estados ───────────────────────────────────────────────────────────────────
BUSQUEDA = "BUSQUEDA"
ORIENTAR = "ORIENTAR"
SEGUIR   = "SEGUIR"
ATAQUE   = "ATAQUE"
EVASION  = "EVASION"

# ── Variables de estado ───────────────────────────────────────────────────────
estado_actual   = BUSQUEDA
search_dir      = 1          # +1 = girar derecha, -1 = izquierda
search_timer    = 0.0        # temporizador para alternar giro de búsqueda
evasion_done    = False      # flag para ejecutar evasión una sola vez por evento

# ── Instancias globales ───────────────────────────────────────────────────────
lidar  = LidarScanner()
vision = VisionSystem(show_debug=True)  # Pon False en competición real


# ── Señal de salida limpia ────────────────────────────────────────────────────
def _shutdown(sig=None, frame=None):
    print("\n[Main] Apagando robot...")
    mot.Stop()
    lidar.stop()
    vision.stop()
    sys.exit(0)

signal.signal(signal.SIGINT,  _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


# ── Funciones de estado ───────────────────────────────────────────────────────

def estado_busqueda():
    """Gira lentamente alternando dirección para barrer 360° con el LiDAR."""
    global search_dir, search_timer

    mot.setVelocidad(VEL_BUSQUEDA)
    if search_dir > 0:
        mot.Derecha()
    else:
        mot.Izquierda()

    # Cada SEARCH_TURN_DURATION segundos alterna de dirección
    if time.time() - search_timer > SEARCH_TURN_DURATION * 6:
        search_dir   *= -1
        search_timer  = time.time()

    print(f"  [BÚSQUEDA] Girando {'→' if search_dir > 0 else '←'}")


def estado_orientar(angle_error):
    """Gira hacia el rival hasta estar razonablemente alineado."""
    mot.setVelocidad(VEL_BUSQUEDA + 20)
    if angle_error > 5:
        mot.Derecha()
        print(f"  [ORIENTAR] Girando DERECHA para alinear (error={angle_error:.1f}°)")
    elif angle_error < -5:
        mot.Izquierda()
        print(f"  [ORIENTAR] Girando IZQUIERDA para alinear (error={angle_error:.1f}°)")
    else:
        mot.Stop()


def estado_seguir(angle_error, rival_offset_px):
    """
    Avanza hacia el rival. Si la cámara lo ve, hace correcciones finas de dirección.
    El LiDAR provee el ángulo grueso; la cámara refina cuando el rival está centrado.
    """
    mot.setVelocidad(VEL_SEGUIR)

    # Corrección combinada: LiDAR (ángulo) + Cámara (offset en píxeles)
    if abs(angle_error) > 15:
        # Error grande → girar mientras avanza
        if angle_error > 0:
            mot.AvanzaDer()
        else:
            mot.AvanzaIzq()
    elif vision.rival_visible and abs(rival_offset_px) > RIVAL_CENTER_MARGIN:
        # Error pequeño pero la cámara ve desviación → corrección suave
        if rival_offset_px > 0:
            mot.AvanzaDer()
        else:
            mot.AvanzaIzq()
    else:
        mot.Avanza()

    print(f"  [SEGUIR] Avanzando | LiDAR err={angle_error:.1f}° | "
          f"Cam off={rival_offset_px:+d}px")


def estado_ataque():
    """Máxima velocidad directo hacia el rival."""
    mot.setVelocidad(VEL_ATAQUE)
    mot.Avanza()
    print("  [ATAQUE] ¡EMPUJE!")


def estado_evasion(line_side):
    """
    Evasión bloqueante: retrocede y gira alejándose del borde.
    Bloquea el bucle durante la maniobra.
    """
    print(f"  [EVASION] ¡BORDE DETECTADO en {line_side}! Retrocediendo...")

    # La dirección de giro es opuesta al lado donde está la línea
    if line_side == "izquierda":
        turn_dir = "derecha"
    elif line_side == "derecha":
        turn_dir = "izquierda"
    else:
        # Línea centrada: el robot está recto sobre el borde → giro grande
        turn_dir = "derecha"

    mot.ejecutar_evasion(
        direccion = turn_dir,
        vel       = VEL_EVASION,
        t_atras   = EVADE_BACK_DURATION,
        t_giro    = EVADE_TURN_DURATION,
    )
    print(f"  [EVASION] Maniobra completada. Girando {turn_dir}.")


# ── Bucle principal ───────────────────────────────────────────────────────────

def seleccionar_estado():
    """
    Determina el estado siguiente según la información de LiDAR y cámara.
    Retorna una tupla (nuevo_estado, datos_extra).
    """
    line_detected = vision.line_detected
    line_side     = vision.line_side
    rival_lidar   = lidar.rival_detected
    rival_dist    = lidar.rival_dist_mm
    angle_error   = lidar.angle_error_deg()
    rival_offset  = vision.rival_offset_px

    # ── PRIORIDAD 1: Evasión de borde ─────────────────────────────────────
    if line_detected:
        return EVASION, {"side": line_side}

    # ── PRIORIDAD 2: LiDAR detecta rival ──────────────────────────────────
    if rival_lidar:
        if rival_dist <= LIDAR_ATTACK_DIST_MM:
            return ATAQUE, {}

        if abs(angle_error) > 15:
            return ORIENTAR, {"angle_error": angle_error}

        return SEGUIR, {"angle_error": angle_error, "rival_offset": rival_offset}

    # ── PRIORIDAD 3: Solo cámara detecta rival (LiDAR no lo ve aún) ──────
    if vision.rival_visible:
        # Orientamos según el offset de la cámara
        cam_angle = rival_offset / 3.2   # Conversión burda px→grados (ajustar)
        return SEGUIR, {"angle_error": cam_angle, "rival_offset": rival_offset}

    # ── Sin información → búsqueda ─────────────────────────────────────────
    return BUSQUEDA, {}


def main():
    global estado_actual, search_timer

    print("=" * 60)
    print("  ROBOT SUMO – Sistema iniciando...")
    print("=" * 60)

    # ── Inicialización ─────────────────────────────────────────────────────
    mot.init_board()
    lidar.start()
    vision.start()

    print("\n[Main] Calibrando fondo (mantén el ring vacío 2 segundos)...")
    time.sleep(1.0)
    vision.calibrate_background()
    time.sleep(1.0)

    print("\n[Main] ¡Listo! El robot comenzará en 3 segundos...")
    time.sleep(3.0)

    mot.setVelocidad(VEL_BUSQUEDA)
    search_timer = time.time()

    # ── Bucle principal ────────────────────────────────────────────────────
    print("\n[Main] INICIO DEL COMBATE\n")
    while True:
        nuevo_estado, datos = seleccionar_estado()

        if nuevo_estado != estado_actual:
            print(f"\n>>> Estado: {estado_actual} → {nuevo_estado}")
            estado_actual = nuevo_estado

        # ── Ejecutar el estado actual ──────────────────────────────────────
        if estado_actual == BUSQUEDA:
            estado_busqueda()

        elif estado_actual == ORIENTAR:
            estado_orientar(datos.get("angle_error", 0))

        elif estado_actual == SEGUIR:
            estado_seguir(
                datos.get("angle_error", 0),
                datos.get("rival_offset", 0),
            )

        elif estado_actual == ATAQUE:
            estado_ataque()

        elif estado_actual == EVASION:
            estado_evasion(datos.get("side", "centro"))
            # Tras evasión, volvemos a búsqueda forzosamente
            estado_actual = BUSQUEDA
            search_timer  = time.time()

        time.sleep(LOOP_SLEEP)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
