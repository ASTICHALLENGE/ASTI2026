# =============================================================================
#  lidar_module.py  –  Gestión del YDLidar
#
#  Funcionalidades:
#   · Filtra los ángulos correspondientes a las 4 barras del propio robot
#   · Detecta el objeto más cercano dentro del rango útil (rival)
#   · Devuelve el ángulo y la distancia del rival para orientar el robot
#   · Se ejecuta en un hilo separado para no bloquear el bucle principal
# =============================================================================

import threading
import math
import time
import ydlidar           # SDK oficial de YDLidar (pip install ydlidar)
from config import (
    LIDAR_PORT,
    OWN_BARS_ANGLE_EXCLUSIONS,
    LIDAR_MIN_DIST_MM,
    LIDAR_MAX_DIST_MM,
)


def _angle_in_exclusion(angle_deg: float, exclusions: list) -> bool:
    """Devuelve True si el ángulo cae dentro de alguna zona excluida."""
    a = angle_deg % 360
    for (start, end) in exclusions:
        if start <= end:
            if start <= a <= end:
                return True
        else:
            # Rango que cruza el 0° (ej. 350-10)
            if a >= start or a <= end:
                return True
    return False


class LidarScanner:
    """
    Wrapper del YDLidar que corre en background y expone:
      · rival_angle_deg   – ángulo del objeto más cercano (0° = frente del robot)
      · rival_dist_mm     – distancia en mm del rival
      · rival_detected    – bool: hay rival dentro del rango configurado
    """

    def __init__(self):
        self._lock             = threading.Lock()
        self._rival_angle      = None   # grados (0-360)
        self._rival_dist       = None   # mm
        self._rival_detected   = False
        self._running          = False
        self._thread           = None

        # Configuración del SDK
        ydlidar.os_init()
        self._laser = ydlidar.CYdLidar()
        self._laser.setlidaropt(ydlidar.LidarPropSerialPort,   LIDAR_PORT)
        self._laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
        self._laser.setlidaropt(ydlidar.LidarPropLidarType,    ydlidar.TYPE_TRIANGLE)
        self._laser.setlidaropt(ydlidar.LidarPropDeviceType,   ydlidar.YDLIDAR_TYPE_SERIAL)
        self._laser.setlidaropt(ydlidar.LidarPropScanFrequency,  10.0)   # Hz
        self._laser.setlidaropt(ydlidar.LidarPropSampleRate,      4)     # kHz
        self._laser.setlidaropt(ydlidar.LidarPropMaxRange,   LIDAR_MAX_DIST_MM / 1000.0)
        self._laser.setlidaropt(ydlidar.LidarPropMinRange,   LIDAR_MIN_DIST_MM / 1000.0)
        self._laser.setlidaropt(ydlidar.LidarPropMaxAngle,    180.0)
        self._laser.setlidaropt(ydlidar.LidarPropMinAngle,   -180.0)
        self._laser.setlidaropt(ydlidar.LidarPropSingleChannel, False)
        self._laser.setlidaropt(ydlidar.LidarPropIntenstiy,   False)

    # ── API pública ──────────────────────────────────────────────────────────

    def start(self):
        """Arranca el hilo de escaneo."""
        ret = self._laser.initialize()
        if not ret:
            raise RuntimeError("[LiDAR] No se pudo inicializar el YDLidar. "
                               "Comprueba el puerto y la alimentación.")
        ret = self._laser.turnOn()
        if not ret:
            raise RuntimeError("[LiDAR] No se pudo encender el motor del LiDAR.")

        self._running = True
        self._thread  = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()
        print("[LiDAR] Escáner iniciado.")

    def stop(self):
        """Detiene el hilo de escaneo y apaga el sensor."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self._laser.turnOff()
        self._laser.disconnecting()
        print("[LiDAR] Escáner detenido.")

    @property
    def rival_detected(self) -> bool:
        with self._lock:
            return self._rival_detected

    @property
    def rival_angle_deg(self):
        """Ángulo en grados donde está el rival (None si no se detecta)."""
        with self._lock:
            return self._rival_angle

    @property
    def rival_dist_mm(self):
        """Distancia en mm al rival (None si no se detecta)."""
        with self._lock:
            return self._rival_dist

    def angle_error_deg(self) -> float:
        """
        Diferencia angular respecto al frente del robot (0°).
        Positivo  → rival a la derecha.
        Negativo  → rival a la izquierda.
        Devuelve 0.0 si no hay rival detectado.
        """
        with self._lock:
            if self._rival_angle is None:
                return 0.0
            # Normaliza al rango (-180, 180]
            err = self._rival_angle % 360
            if err > 180:
                err -= 360
            return err

    # ── Lógica interna ───────────────────────────────────────────────────────

    def _scan_loop(self):
        scan = ydlidar.LaserScan()
        while self._running:
            ok = self._laser.doProcessSimple(scan)
            if not ok:
                time.sleep(0.05)
                continue

            best_dist  = float("inf")
            best_angle = None

            for point in scan.points:
                dist_mm   = point.range * 1000.0          # m → mm
                angle_deg = math.degrees(point.angle) % 360

                # 1) Descartar lecturas fuera del rango útil
                if dist_mm < LIDAR_MIN_DIST_MM or dist_mm > LIDAR_MAX_DIST_MM:
                    continue

                # 2) Descartar ángulos correspondientes a las barras del robot
                if _angle_in_exclusion(angle_deg, OWN_BARS_ANGLE_EXCLUSIONS):
                    continue

                # 3) Quedarse con el punto más cercano (= rival)
                if dist_mm < best_dist:
                    best_dist  = dist_mm
                    best_angle = angle_deg

            with self._lock:
                if best_angle is not None:
                    self._rival_angle    = best_angle
                    self._rival_dist     = best_dist
                    self._rival_detected = True
                else:
                    self._rival_angle    = None
                    self._rival_dist     = None
                    self._rival_detected = False
