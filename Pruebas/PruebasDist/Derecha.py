import time
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)

# 26cm en 1 seg

Omni.setVelocidad(130)

Omni.Derecha()
time.sleep(1)
Omni.Stop()