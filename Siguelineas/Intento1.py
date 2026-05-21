import threading # Para que el codigo vea mas de una cosa a la vez
import cv2

import sys
sys.path.append('/home/asti/CodigosRobot')
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
    # Cuento los pixeles blancos en el thresh (Negros en la camara) en cada zona
    contIzq = cv2.countNonZero(izq)
    contMedio = cv2.countNonZero(medio)
    contDer = cv2.countNonZero(der)

# 1. Definimos cu�ntos p�xeles m�nimos son necesarios para considerar que "hay una l�nea"
#    (Tendr�s que ajustar este valor dependiendo del grosor de tu l�nea y la altura de la c�mara)
    umbral = 400 

    hay_izq = contIzq > umbral
    hay_medio = contMedio > umbral
    hay_der = contDer > umbral

# 2. Hago movimientos basados en un SISTEMA DE PRIORIDADES
    if hay_medio:
        # Prioridad 1: Si hay l�nea en el centro, avanza. 
        # Esto hace que en un cruce en "+" el robot ignore los lados y siga recto.
        Movimiento.Avanza()
        print("L�nea en medio")
        cont = 0
        
    elif hay_izq:
        # Prioridad 2: Si no hay l�nea en el centro (ej. una "T"), giramos siempre a la izquierda.
        # Al darle prioridad a un lado, evitas que se quede paralizado sin saber qu� hacer.
        Movimiento.Izquierda()
        print("L�nea a la izquierda")
        cont = 0
        
    elif hay_der:
        # Prioridad 3: Si solo hay l�nea a la derecha, giramos a la derecha.
        Movimiento.Derecha()
        print("L�nea a la derecha")
        cont = 0
        
    else: 
        # Si no detecta l�nea en ninguna parte (todas est�n por debajo del umbral)
        if cont < 20:
            Movimiento.Atras()
            cont += 1
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
Movimiento.Stop()
Movimiento.setVelocidad(0)

