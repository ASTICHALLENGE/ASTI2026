import time
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)

# =====================================================================
# CALIBRACI�N DE TRACCI�N (AQU� EST� LA MAGIA)
# =====================================================================
# MULT_DELANTE: Porcentaje de fuerza para las ruedas delanteras (65%)
# MULT_ATRAS: Porcentaje de fuerza para las ruedas traseras (145%)
# Al darle m�s fuerza a las de atr�s, evitamos que el culo del robot se quede rezagado.
MULT_DELANTE = 0.65  
MULT_ATRAS   = 1.45  
# =====================================================================

def set_motor(pinA, pinR, pwm):
    pwm = max(-255, min(255, int(pwm)))
    if pwm >= 0:
        board.pwm_write(pinA, pwm)
        board.pwm_write(pinR, 0)
    else:
        board.pwm_write(pinA, 0)
        board.pwm_write(pinR, -pwm)

def trazar_vector(pwm_x, pwm_y, duracion):
    """
    pwm_y (Adelante/Atr�s) no se altera porque en tu robot funciona bien.
    pwm_x (Laterales) se multiplica por la compensaci�n para que no rote.
    """
    fuerza_x_delante = pwm_x * MULT_DELANTE
    fuerza_x_atras   = pwm_x * MULT_ATRAS

    m11 = pwm_y + fuerza_x_delante  # Izquierda Arriba
    m12 = pwm_y - fuerza_x_atras    # Izquierda Abajo
    m21 = pwm_y - fuerza_x_delante  # Derecha Arriba
    m22 = pwm_y + fuerza_x_atras    # Derecha Abajo

    set_motor(Omni.mot11A, Omni.mot11R, m11)
    set_motor(Omni.mot12A, Omni.mot12R, m12)
    set_motor(Omni.mot21A, Omni.mot21R, m21)
    set_motor(Omni.mot22A, Omni.mot22R, m22)

    time.sleep(duracion)
    Omni.Stop()
    time.sleep(0.5)

print("Trazando tri�ngulo compensando el peso del chasis...")

# Usamos un PWM base un poco m�s alto (140) para que las ruedas 
# delanteras no se queden atascadas al reducirles la fuerza al 65%.
# 140 de PWM durante 0.9 segundos te dar� aproximadamente los 25 cm.
VEL = 140 
TIEMPO = 0.9 

# Lado 1: Derecha (0�)
# X recibe toda la velocidad, Y est� a 0
print("Lado 1...")
trazar_vector(VEL, 0, TIEMPO)

# Lado 2: Diagonal Arriba-Izquierda (120�)
# Matem�ticamente: X es -65% (izquierda), Y es 86.6% (arriba)
print("Lado 2...")
trazar_vector(-VEL * 0.5, VEL * 0.866, TIEMPO)

# Lado 3: Diagonal Abajo-Izquierda (240�)
# Matem�ticamente: X es -65% (izquierda), Y es -86.6% (abajo)
print("Lado 3...")
trazar_vector(-VEL * 0.5, -VEL * 0.866, TIEMPO)

print("�Hecho!")
board.shutdown()