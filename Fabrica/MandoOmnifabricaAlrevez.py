import evdev # Para traducir el control de play
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

from pymata4 import pymata4
board = pymata4.Pymata4()
Omni.init_motores(board)
servo = 20
board.set_pin_mode_servo(servo)

try:
    mando = evdev.InputDevice('/dev/input/event5')
    print("Conectado")
except:
    print("Error de conexion al control")
    exit()


joyX = 0
joyY = 0
joyRX = 0
vel = 130
apagado = False
R2 = 0
L2 = 0

# NUEVO: Variable para recordar qué está haciendo el robot y no repetir la orden
movimiento_actual = "STOP"
movimientoGarra = "STOP"

try:
    for evento in mando.read_loop():
        # ============ BOTONES NORMALES ============
        if evento.type == evdev.ecodes.EV_KEY:
            if evento.code == evdev.ecodes.BTN_MODE and evento.value == 1:
                if apagado == True:
                    apagado = False
                    vel = 130
                    print("Prendido")
                else:
                    apagado = True
                    vel = 0
                    Omni.Stop()
                    movimiento_actual = "STOP"
                    print("Apagado")
                    
        if apagado == False:
            if evento.type == evdev.ecodes.EV_KEY:
                # Cdigo para aumentar velocidad con R1 y bajar con L1
                # Le añadimos "evento.value == 1" para que solo cambie al presionar, no al soltar
                if evento.code == evdev.ecodes.BTN_TR and evento.value == 1: # R1
                    vel += 10
                    if vel > 255: vel = 255
                    Omni.setVelocidad(vel)
                    print("mas velocidad:", vel)
                elif evento.code == evdev.ecodes.BTN_TL and evento.value == 1: # L1
                    vel -= 10
                    if vel < 0: vel = 0
                    Omni.setVelocidad(vel)
                    print("menos velocidad:", vel)

            # ============ JOYSTICKS Y GATILLOS ============
            if evento.type == evdev.ecodes.EV_ABS: 
                # 1. Primero actualizamos todas las variables del mando
                if evento.code == evdev.ecodes.ABS_RZ: 
                    R2 = evento.value
                elif evento.code == evdev.ecodes.ABS_Z: 
                    L2 = evento.value
                elif evento.code == evdev.ecodes.ABS_RX: 
                    joyRX = (evento.value - 128) / 1.28
                elif evento.code == evdev.ecodes.ABS_X: 
                    joyX = (evento.value - 128) / 1.28      
                elif evento.code == evdev.ecodes.ABS_Y: 
                    joyY = (128 - evento.value) / 1.28

                # 3. Calculamos cuál DEBERÍA ser el movimiento, pero lo guardamos en una variable
                nuevo_movimiento = "STOP"
                
                if R2 > 0:
                    nuevoMovimientoGarra = "ABRIR"
                elif L2 > 0:
                    nuevoMovimientoGarra = "CERRAR"
                else:
                    nuevoMovimientoGarra = "STOP"

                if joyY > 50:
                    if joyX > 50: nuevo_movimiento = "ADELANTE_DER"
                    elif joyX < -50: nuevo_movimiento = "ADELANTE_IZQ"
                    else: nuevo_movimiento = "ADELANTE"
                elif joyY < -50:
                    if joyX > 50: nuevo_movimiento = "ATRAS_DER"
                    elif joyX < -50: nuevo_movimiento = "ATRAS_IZQ"
                    else: nuevo_movimiento = "ATRAS"
                elif joyX > 50:
                    nuevo_movimiento = "GIRO_DER"
                elif joyX < -50:
                    nuevo_movimiento = "GIRO_IZQ"
                elif joyRX > 50:
                    nuevo_movimiento = "DERECHA"
                elif joyRX < -50:
                    nuevo_movimiento = "IZQUIERDA"
                else:
                    nuevo_movimiento = "STOP"

                # 4. EL TRUCO: Solo le enviamos la orden al robot si la dirección HA CAMBIADO
                if nuevo_movimiento != movimiento_actual:
                    if nuevo_movimiento == "IZQUIERDA": Omni.Izquierda()
                    elif nuevo_movimiento == "DERECHA": Omni.Derecha()
                    elif nuevo_movimiento == "ADELANTE_DER": Omni.AvanzaDer()
                    elif nuevo_movimiento == "ADELANTE_IZQ": Omni.AvanzaIzq()
                    elif nuevo_movimiento == "ADELANTE": Omni.Avanza()
                    elif nuevo_movimiento == "ATRAS_DER": Omni.AtrasDer()
                    elif nuevo_movimiento == "ATRAS_IZQ": Omni.AtrasIzq()
                    elif nuevo_movimiento == "ATRAS": Omni.Atras()
                    elif nuevo_movimiento == "GIRO_DER": Omni.GiroDer()
                    elif nuevo_movimiento == "GIRO_IZQ": Omni.GiroIzq()
                    elif nuevo_movimiento == "STOP": Omni.Stop()

                    movimiento_actual = nuevo_movimiento
                    print(nuevo_movimiento) # La consola también estará mucho más limpia

                if movimientoGarra != nuevoMovimientoGarra:
                    if nuevoMovimientoGarra == "ABRIR": board.servo_write(servo,180)
                    elif nuevoMovimientoGarra == "CERRAR": board.servo_write(servo,0)
                    elif nuevoMovimientoGarra == "STOP": board.servo_write(servo, 95)
                    movimientoGarra = nuevoMovimientoGarra
                    print(nuevoMovimientoGarra) 

                    
                    # Guardamos el nuevo movimiento para no repetirlo la próxima vez


except KeyboardInterrupt:
    print("Deten con ctrl+c")
    Omni.Stop()
    Omni.board.shutdown()