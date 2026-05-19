
import evdev # Para traducir el control de play
import threading # Para que el codigo vea mas de una cosa a la vez

import sys
sys.path.append('/home/asti/CodigosRobot')
import Omni

try:
    mando = evdev.InputDevice('/dev/input/event5')
    print("Conectado")
except:
    print("Error de conexion al control")
    exit()

joyX=0
joyY=0
joyRX=0
vel = 130
apagado = False
R2 = 0
L2 = 0
gatillo = False



try:
    for evento in mando.read_loop():
        if R2<=5 and L2<=5: gatillo=False
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
                        Omni.Stop()
                        print("Apagado")
        if apagado == False:
            if evento.type == evdev.ecodes.EV_KEY:
            # Cdigo para aumentar velocidad con R1 y bajar con L1
                if evento.code == evdev.ecodes.BTN_TR: # R1
                    vel+=10
                    if vel>255:
                        vel=255
                    Omni.setVelocidad(vel)
                    print("mas velocidad")
                    print(vel)
                elif (evento.code == evdev.ecodes.BTN_TL ): # L1
                    vel-=10
                    if vel<0:
                        vel=0
                    Omni.setVelocidad(vel)
                    print("menos velocidad")
                    print(vel)
                

            if evento.type == evdev.ecodes.EV_ABS: #EV_ABS detecta joysticks y gatillos
                #Codigo para controlar velocidad con R2
                if (evento.code == evdev.ecodes.ABS_RZ ): # Gatillo derecho
                    print("R2")
                    gatillo = True
                    R2 = evento.value
                elif evento.code == evdev.ecodes.ABS_Z: # Gatillo izquierdo
                    print("L2")
                    gatillo = True
                    L2=evento.value
                if evento.code == evdev.ecodes.ABS_RX: #Joystick derecho
                    joyRX = (evento.value - 128) / 1.28
                if L2>0 or joyRX<-50:
                    Omni.Izquierda()
                    print("Izquierda")
                elif R2>0 or joyRX>50:
                    Omni.Derecha()
                    print("Derecha")


                if evento.code == evdev.ecodes.ABS_X:
                    joyX = (evento.value - 128) / 1.28      # Operacion para cambiar a valores de -100 a 100
                elif evento.code == evdev.ecodes.ABS_Y:
                    joyY = (128 - evento.value) / 1.28
                if gatillo==False:
                    Omni.setVelocidad(vel)
                    if (joyY>50):
                        if(joyX>50):
                            Omni.AvanzaDer()
                            print("Adelante derecha")
                        elif(joyX<-50):
                            Omni.AvanzaIzq()
                            print("Adelante izquierda")
                        else:
                            Omni.Avanza()
                            print("Adelante")
                    elif (joyY<-50):
                        if(joyX>50):
                            Omni.AtrasDer()
                            print("Atras derecha")
                        elif(joyX<-50):
                            Omni.AtrasIzq()
                            print("Atras izquierda")
                        else:
                            Omni.Atras()
                            print("Atras joystick")
                    elif(joyX>50):
                        Omni.GiroDer()
                        print("Giro Derecha")
                    elif(joyX<-50):
                        Omni.GiroIzq()
                        print("Giro Izquierda")
                    else:
                        Omni.Stop()
                        # print("Stop")
                else:
                    if R2>0:
                        if(joyX>50):
                            Omni.AvanzaDer()
                            print("Avanza Derecha")
                        elif(joyX<-50):
                            Omni.AvanzaIzq()
                            print("Avanza Izquierda")
                        else:
                            Omni.Avanza()
                            print("Avanza")
                    elif L2>0:
                        if(joyX>50):
                            Omni.AtrasDer()
                            print("Atras Derecha")
                        elif(joyX<-50):
                            Omni.AtrasIzq()
                            print("Atras Izquierda")
                        else:
                            Omni.Atras()
                            print("Atras gatillo")




except KeyboardInterrupt:
    print("Deten con ctrl+c")
    Omni.Stop()
    Omni.board.shutdown()


