import time
import cv2

import sys
sys.path.append('/home/asti/CodigosRobot')
import Movimiento as mov

from pymata4 import pymata4
import time
board = pymata4.Pymata4()

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error al conectar la camara")
    exit()

mov.setVelocidad(130)

servoIzq = 20
servoDer = 23

board.set_pin_mode_servo(servoIzq)
board.set_pin_mode_servo(servoDer)

time.sleep(0.5) # Damos tiempo para que se estabilicen las primeras lecturas

board.servo_write(servoIzq, 20)
board.servo_write(servoDer, 180)

while True:
    ret1, frame = cam.read() # Tomo la foto
    if not ret1:
        print("Error al tomar la foto")
        break # No uso exit para que no pare todo el codigo y llegue a la parte donde se borra todo

    crop = frame[200:480, 0:640] # Hago la imagen un poco mas pequeña
    gr = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) # Paso la foto a blanco y negro
    gauss = cv2.GaussianBlur(gr, (3, 3), 0)
    canny = cv2.Canny(gauss, 50, 150)
    (contornos,_) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(crop,contornos,-1,(0,0,255), 2)
    
    zonaIzq = 256 
    zonaDer = 384

    izq = canny[:, 0:zonaIzq]
    medio = canny[:, zonaIzq:zonaDer]
    der = canny[:, zonaDer:640]

    pixIzq = cv2.countNonZero(izq)
    pixMed = cv2.countNonZero(medio)
    pixDer = cv2.countNonZero(der)

    if pixMed > pixDer and pixMed > pixIzq:
        mov.Avanza()
        time.sleep(2)
        mov.Atras()
        time.sleep(2)
    elif pixIzq > pixMed:
        mov.Izquierda()
    else:
        mov.Derecha()
    
    cv2.imshow("contornos", crop)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): # Para que cuando le de a la 'q' pare 
        break

cam.release() #Para dejar de usar la camara
cv2.destroyAllWindows() #Para cerrar las pestanas
mov.Stop()
mov.setVelocidad(0)