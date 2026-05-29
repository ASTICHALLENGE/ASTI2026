import cv2
import sys
sys.path.append('/home/asti/CodigosRobot')
import Movimiento
from pymata4 import pymata4

board = pymata4.Pymata4()
Movimiento.init_motores(board)

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error al conectar la camara")
    exit()

# --- Par�metros ajustables ---
Kp = 0.35          # Ganancia proporcional (cu�nto girar por cada pixel de error)
VEL_BASE = 130     # Velocidad base hacia adelante
VEL_MIN = 80       # Velocidad m�nima en giro cerrado
UMBRAL = 400       # P�xeles m�nimos para considerar que hay l�nea
PERDIDA_MAX = 30   # Frames sin l�nea antes de parar

# ROI cercano (control fino) y lejano (anticipaci�n de curva)
ROI_CERCA_Y1, ROI_CERCA_Y2 = 280, 480
ROI_LEJOS_Y1, ROI_LEJOS_Y2 = 150, 280

Movimiento.setVelocidad(VEL_BASE)

# Estado
last_dir = "der"   # Memoria de la �ltima direcci�n conocida
frames_sin_linea = 0

def calcular_centroide(roi_thresh):
    """Devuelve la posici�n X del centroide de la l�nea, o None si no hay l�nea."""
    M = cv2.moments(roi_thresh)
    if M["m00"] > UMBRAL:
        return int(M["m10"] / M["m00"])
    return None

def lado_dominante(roi_thresh):
    """Devuelve 'izq', 'der' o None seg�n d�nde haya m�s p�xeles en el ROI."""
    mitad = roi_thresh.shape[1] // 2
    pixeles_izq = cv2.countNonZero(roi_thresh[:, :mitad])
    pixeles_der = cv2.countNonZero(roi_thresh[:, mitad:])
    if pixeles_izq < UMBRAL and pixeles_der < UMBRAL:
        return None
    return "izq" if pixeles_izq > pixeles_der else "der"

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error al tomar la foto")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

    # Recortar los dos ROIs
    roi_cerca = thresh[ROI_CERCA_Y1:ROI_CERCA_Y2, 0:640]
    roi_lejos = thresh[ROI_LEJOS_Y1:ROI_LEJOS_Y2, 0:640]

    # 1. Calcular centroide en ROI cercano
    cx = calcular_centroide(roi_cerca)

    # 2. El ROI lejano actualiza la memoria de direcci�n mientras haya l�nea
    lado_lejos = lado_dominante(roi_lejos)
    if lado_lejos is not None:
        last_dir = lado_lejos

    # 3. Decisi�n de movimiento
    if cx is not None:
        # HAY L�NEA: control proporcional
        error = cx - 320          # Centro de imagen = 320px
        giro = int(Kp * error)

        vel_izq = max(VEL_MIN, VEL_BASE + giro)
        vel_der = max(VEL_MIN, VEL_BASE - giro)

        # Clamp para no pasarse de 255
        vel_izq = min(255, vel_izq)
        vel_der = min(255, vel_der)

        Movimiento.setVelocidades(vel_izq, vel_der)
        frames_sin_linea = 0
        print(f"L�nea en cx={cx} | error={error} | L={vel_izq} D={vel_der}")

    else:
        # SIN L�NEA: girar hacia el �ltimo lado conocido (recuperaci�n activa)
        frames_sin_linea += 1

        if frames_sin_linea < PERDIDA_MAX:
            if last_dir == "izq":
                Movimiento.Izquierda()
                print(f"Buscando (giro izq) | frame {frames_sin_linea}")
            else:
                Movimiento.Derecha()
                print(f"Buscando (giro der) | frame {frames_sin_linea}")
        else:
            Movimiento.Stop()
            print("Robot perdido � detenido")

    # Visualizaci�n con l�neas de ROI dibujadas
    cv2.line(frame, (0, ROI_CERCA_Y1), (640, ROI_CERCA_Y1), (0, 255, 0), 1)
    cv2.line(frame, (0, ROI_LEJOS_Y1), (640, ROI_LEJOS_Y1), (255, 255, 0), 1)
    if cx is not None:
        cv2.circle(frame, (cx, (ROI_CERCA_Y1 + ROI_CERCA_Y2) // 2), 8, (0, 0, 255), -1)

    cv2.imshow("Camara", frame)
    cv2.imshow("Thresh cerca", roi_cerca)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
Movimiento.Stop()
Movimiento.setVelocidad(0)