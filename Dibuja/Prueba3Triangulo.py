import time
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)

# =====================================================================
# VARIABLE �NICA DE CALIBRACI�N (YAW INJECTION)
# =====================================================================
# Si el robot, al ir a la derecha, se tuerce en sentido HORARIO (derecha):
#   -> Pon un valor negativo, por ejemplo: -0.15, -0.20 o -0.30
# Si el robot se tuerce en sentido ANTIHORARIO (izquierda):
#   -> Pon un valor positivo, por ejemplo: 0.15, 0.20 o 0.30
K_YAW = 0.00 
# =====================================================================

def set_motor(pinA, pinR, pwm):
    pwm = max(-255, min(255, int(pwm)))
    if pwm >= 0:
        board.pwm_write(pinA, pwm)
        board.pwm_write(pinR, 0)
    else:
        board.pwm_write(pinA, 0)
        board.pwm_write(pinR, -pwm)

def prueba_lateral():
    vel_x = 130  # Velocidad lateral constante
    vel_y = 0    # Sin movimiento adelante/atr�s
    
    # Inyectamos el vector de giro opuesto al derrape mec�nico
    compensacion_giro = vel_x * K_YAW 

    # Matriz Cinem�tica Pura de Mecanum
    m11 = vel_y + vel_x + compensacion_giro  # Izquierda Arriba
    m12 = vel_y - vel_x + compensacion_giro  # Izquierda Abajo
    m21 = vel_y - vel_x - compensacion_giro  # Derecha Arriba
    m22 = vel_y + vel_x - compensacion_giro  # Derecha Abajo

    set_motor(Omni.mot11A, Omni.mot11R, m11)
    set_motor(Omni.mot12A, Omni.mot12R, m12)
    set_motor(Omni.mot21A, Omni.mot21R, m21)
    set_motor(Omni.mot22A, Omni.mot22R, m22)

    time.sleep(1.5)
    Omni.Stop()

print(f"Probando desplazamiento lateral con K_YAW = {K_YAW}")
prueba_lateral()
board.shutdown()