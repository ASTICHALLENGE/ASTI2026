import time
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)

Omni.setVelocidad(130)

Omni.Avanza()
time.sleep(0.25)

Omni.Stop()
Omni.setVelocidad(110)
time.sleep(0.5)

Omni.Derecha()
time.sleep(1.15)

Omni.Stop()
Omni.setVelocidad(130)
time.sleep(0.5)

Omni.Atras()
time.sleep(0.25)

Omni.Stop()
Omni.setVelocidad(110)
time.sleep(0.5)

Omni.Izquierda()
time.sleep(1.15)
Omni.Stop()