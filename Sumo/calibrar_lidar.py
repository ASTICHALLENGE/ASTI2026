# =============================================================================
#  calibrar_lidar.py  –  Herramienta de calibración de las barras del LiDAR
#
#  CÓMO USAR:
#   1. Pon el robot en el suelo, en zona despejada (sin paredes cercanas <1.5m)
#   2. Ejecuta: python3 calibrar_lidar.py
#   3. Verás en tiempo real los ángulos donde el LiDAR detecta objetos cercanos
#   4. Los ángulos que aparecen SIEMPRE son las barras de tu robot
#   5. Copia esos rangos en OWN_BARS_ANGLE_EXCLUSIONS en config.py
# =============================================================================

import math
import time
import ydlidar
from config import LIDAR_PORT, LIDAR_MIN_DIST_MM

BARRA_MAX_DIST_MM = 400   # Distancia máxima para considerar que es una barra


def main():
    ydlidar.os_init()
    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort,     LIDAR_PORT)
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
    laser.setlidaropt(ydlidar.LidarPropLidarType,      ydlidar.TYPE_TRIANGLE)
    laser.setlidaropt(ydlidar.LidarPropDeviceType,     ydlidar.YDLIDAR_TYPE_SERIAL)
    laser.setlidaropt(ydlidar.LidarPropScanFrequency,  10.0)
    laser.setlidaropt(ydlidar.LidarPropSampleRate,     4)
    laser.setlidaropt(ydlidar.LidarPropMaxRange,       2.0)
    laser.setlidaropt(ydlidar.LidarPropMinRange,       LIDAR_MIN_DIST_MM / 1000.0)
    laser.setlidaropt(ydlidar.LidarPropMaxAngle,       180.0)
    laser.setlidaropt(ydlidar.LidarPropMinAngle,      -180.0)
    laser.setlidaropt(ydlidar.LidarPropSingleChannel,  False)
    laser.setlidaropt(ydlidar.LidarPropIntenstiy,      False)

    if not laser.initialize():
        print("[ERROR] No se pudo inicializar el LiDAR.")
        return
    if not laser.turnOn():
        print("[ERROR] No se pudo encender el motor del LiDAR.")
        return

    print("\n=== CALIBRACIÓN DE BARRAS DEL ROBOT ===")
    print(f"Mostrando ángulos con objetos a menos de {BARRA_MAX_DIST_MM} mm\n")
    print("Presiona Ctrl+C para terminar.\n")

    scan = ydlidar.LaserScan()
    # Acumulador para ver qué ángulos aparecen repetidamente
    angle_hits = {}

    try:
        while True:
            ok = laser.doProcessSimple(scan)
            if not ok:
                continue

            current_angles = []
            for point in scan.points:
                dist_mm   = point.range * 1000.0
                angle_deg = round(math.degrees(point.angle) % 360, 1)

                if LIDAR_MIN_DIST_MM < dist_mm < BARRA_MAX_DIST_MM:
                    current_angles.append((angle_deg, dist_mm))
                    angle_hits[angle_deg] = angle_hits.get(angle_deg, 0) + 1

            if current_angles:
                current_angles.sort(key=lambda x: x[0])
                print("\rÁngulos cercanos (°):  ", end="")
                for ang, dist in current_angles:
                    print(f"  {ang:6.1f}° @ {dist:4.0f}mm", end="")
                print("   ", end="", flush=True)

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n\n=== RESUMEN – Ángulos detectados frecuentemente ===")
        # Ordena por frecuencia de aparición
        sorted_hits = sorted(angle_hits.items(), key=lambda x: -x[1])
        top = [(a, c) for a, c in sorted_hits if c > 5][:20]
        print(f"{'Ángulo (°)':>12}  {'Apariciones':>12}")
        for ang, count in top:
            print(f"{ang:>12.1f}  {count:>12}")
        print("\nAgrupa los ángulos consecutivos en rangos y")
        print("ponlos en OWN_BARS_ANGLE_EXCLUSIONS en config.py")

    finally:
        laser.turnOff()
        laser.disconnecting()


if __name__ == "__main__":
    main()
