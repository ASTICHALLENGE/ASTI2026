
import evdev # Para traducir el control de play
import threading # Para que el codigo vea mas de una cosa a la vez

import sys
sys.path.append('/home/asti/CodigosRobot')
import MovimientoAlrevez as Movimiento

from pymata4 import pymata4
board = pymata4.Pymata4()
Movimiento.init_motores(board)

try:
    mando = evdev.InputDevice('/dev/input/event5')
    print("Conectado")
except:
    print("Error de conexion al control")
    exit()

joyX=0
joyY=0
vel = 130
apagado = False
R2 = 0
L2 = 0
servo = 20
board.set_pin_mode_servo(servo)



try:
    for evento in mando.read_loop():
        if evento.type == evdev.ecodes.EV_KEY:
            if evento.code == evdev.ecodes.BTN_MODE:
                if evento.value == 1:
                    if apagado == True:
                        apagado = False
                        vel = 130
                        print("Prendido")
                    else:
                        apagado = True
                        vel = 0
                        Movimiento.Stop()
                        print("Apagado")
        if apagado == False:
            if evento.type == evdev.ecodes.EV_KEY:
            # Cdigo para aumentar velocidad con R1 y bajar con L1
                if evento.code == evdev.ecodes.BTN_TR: # R1
                    vel+=10
                    if vel>255:
                        vel=255
                    Movimiento.setVelocidad(vel)
                    print("mas velocidad")
                    print(vel)
                elif (evento.code == evdev.ecodes.BTN_TL ): # L1
                    vel-=10
                    if vel<0:
                        vel=0
                    Movimiento.setVelocidad(vel)
                    print("menos velocidad")
                    print(vel)
                

            if evento.type == evdev.ecodes.EV_ABS: #EV_ABS detecta joysticks y gatillos
                #Codigo para controlar velocidad con R2
                if (evento.code == evdev.ecodes.ABS_RZ ): # Gatillo derecho
                    R2 = evento.value
                elif evento.code == evdev.ecodes.ABS_Z:
                    L2=evento.value
                if R2>0:
                    board.servo_write(servo, 180)
                    print("Abre garra")
                elif L2>0:
                    board.servo_write(servo, 0)
                    print("Cierra garra")
                elif L2==0 and R2==0:
                    board.servo_write(servo, 95)
                    print("Stop garra")
                if evento.code == evdev.ecodes.ABS_X:
                    joyX = (evento.value - 128) / 1.28      # Operacion para cambiar a valores de -100 a 100
                elif evento.code == evdev.ecodes.ABS_Y:
                    joyY = (128 - evento.value) / 1.28
                    Movimiento.setVelocidad(vel)
                    if (joyY>50):
                        if(joyX>50):
                            Movimiento.AvanzaDer()
                            print("Adelante derecha")
                        elif(joyX<-50):
                            Movimiento.AvanzaIzq()
                            print("Adelante izquierda")
                        else:
                            Movimiento.Avanza()
                            print("Adelante")
                    elif (joyY<-50):
                        if(joyX>50):
                            Movimiento.AtrasDer()
                            print("Atras derecha")
                        elif(joyX<-50):
                            Movimiento.AtrasIzq()
                            print("Atras izquierda")
                        else:
                            Movimiento.Atras()
                            print("Atras joystick")
                    elif(joyX>50):
                        Movimiento.Derecha()
                        print("Derecha")
                    elif(joyX<-50):
                        Movimiento.Izquierda()
                        print("Izquierda")
                    else:
                        Movimiento.Stop()
                        # print("Stop")




except KeyboardInterrupt:
    print("Deten con ctrl+c")
    Movimiento.Stop()
    Movimiento.board.shutdown()


