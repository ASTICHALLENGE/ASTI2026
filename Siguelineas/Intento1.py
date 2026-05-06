import threading # Para que el codigo vea mas de una cosa a la vez
import cv2

import sys
sys.path.append('/home/r2-team2/Robot')
import Movimiento

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error al conectar la camara")
    exit()

cont = 0
Movimiento.setVelocidad(130)

while True:

    ret1, frame = cam.read() # Tomo la foto
    if not ret1:
        print("Error al tomar la foto")
        break # No uso exit para que no pare todo el codigo y llegue a la parte donde se borra todo

    crop = frame[200:480, 0:640] # Hago la imagen un poco ms pqueÃ±a 


    gr = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) # Paso la foto a blanco y negro


    ret2, thresh = cv2.threshold(gr, 60, 255, cv2.THRESH_BINARY_INV) #Invierto los colores de la foto en blanco y negro para que lo negro salga blanco

#Separo en tres zonas en 40% izq, 20% medio y 40% der
    zonaIzq = 256 
    zonaDer = 384

    izq = thresh[:, 0:zonaIzq]
    medio = thresh[:, zonaIzq:zonaDer]
    der = thresh[:, zonaDer:640]

#Cuento los pixeles blancos en el thresh (Negros en la camara) en cada zona
    contIzq = cv2.countNonZero(izq)
    contMedio = cv2.countNonZero(medio)
    contDer = cv2.countNonZero(der)

#Hago movimientos segun donde haya mas
    if contIzq > contMedio and contIzq > contDer:
        Movimiento.Izquierda()
        print("Linea a la izquierda")
        cont=0
    elif contDer > contIzq and contDer > contMedio:
        Movimiento.Derecha()
        print("Linea a la derecha")
        cont=0
    elif contMedio > contIzq and contMedio > contDer:
        Movimiento.Avanza()
        print("Linea en medio")
        cont=0
    else: #Si no detecta linea va sumando en un contador y si llega a 100 ciclos el robot se quedara parado
        if cont<20:
            Movimiento.Atras()
            cont+=1
            print("Pa atras buscando linea")
            print(cont)
        else:
            Movimiento.Stop()
            print("Robot perdido")
        




    cv2.imshow("Foto", frame) # Pra ver lo que ve la camara
    cv2.imshow("Blanco/Negro", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'): # Para que cuando le de a la 'q' pare 
        break

cam.release() #Para dejar de usar la camara
cv2.destroyAllWindows() #Para cerrar las pestanas
Movimiento.stop()
Movimiento.setVelocidad(0)

