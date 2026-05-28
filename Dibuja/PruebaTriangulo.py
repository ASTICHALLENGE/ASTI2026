import time
import math
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)

# Funci�n auxiliar para enviar el PWM exacto a cada par de pines
def set_motor(pinA, pinR, vel_motor):
    if vel_motor >= 0:
        board.pwm_write(pinA, int(vel_motor))
        board.pwm_write(pinR, 0)
    else:
        board.pwm_write(pinA, 0)
        board.pwm_write(pinR, int(-vel_motor))

# El "cerebro" holon�mico
def mover_holonomico(angulo_grados, velocidad_max, duracion):
    # Angulo 0 = Derecha, Angulo 90 = Adelante
    rad = math.radians(angulo_grados)
    vx = math.cos(rad)
    vy = math.sin(rad)

    # Ecuaciones cinem�ticas para la configuraci�n X-Drive
    fl = vy + vx  # mot11 (Izquierda Arriba)
    fr = vy - vx  # mot21 (Derecha Arriba)
    bl = vy - vx  # mot12 (Izquierda Abajo)
    br = vy + vx  # mot22 (Derecha Abajo)

    # Encontrar el valor m�ximo para normalizar
    max_val = max(abs(fl), abs(fr), abs(bl), abs(br))
    if max_val == 0: max_val = 1
    
    # Repartir la velocidad proporcionalmente a cada rueda
    fl = (fl / max_val) * velocidad_max
    fr = (fr / max_val) * velocidad_max
    bl = (bl / max_val) * velocidad_max
    br = (br / max_val) * velocidad_max

    # Mandar los pulsos usando las variables de pines exportadas por OmniAlrevez
    set_motor(Omni.mot11A, Omni.mot11R, fl)
    set_motor(Omni.mot21A, Omni.mot21R, fr)
    set_motor(Omni.mot12A, Omni.mot12R, bl)
    set_motor(Omni.mot22A, Omni.mot22R, br)

    time.sleep(duracion)
    Omni.Stop()
    time.sleep(0.5) # Pausa para asentar las inercias del chasis

print("Dibujando Tri�ngulo Holon�mico...")

V_CONSTANTE = 130
TIEMPO_LADO = 1.5

# Lado 1: Hacia la derecha (0 grados)
mover_holonomico(0, V_CONSTANTE, TIEMPO_LADO)

# Lado 2: Diagonal arriba-izquierda (120 grados)
mover_holonomico(120, V_CONSTANTE, TIEMPO_LADO)

# Lado 3: Diagonal abajo-izquierda (240 grados) para cerrar
mover_holonomico(240, V_CONSTANTE, TIEMPO_LADO)

print("Tri�ngulo terminado.")
board.shutdown()