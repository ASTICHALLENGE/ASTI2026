import time
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)
# 32cm en 1 segundo

Omni.setVelocidad(130)

Omni.Avanza()
time.sleep(1)
Omni.Stop()