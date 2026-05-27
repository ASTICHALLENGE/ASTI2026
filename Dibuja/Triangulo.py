import time
from pymata4 import pymata4
import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

board = pymata4.Pymata4()
Omni.init_motores(board)

Omni.setVelocidad(130)

Omni.AvanzaDer()
time.sleep(1.2)

Omni.Stop()
time.sleep(0.5)

Omni.GiroDer()
time.sleep(0.3)

Omni.Stop()
time.sleep(0.5)

Omni.AtrasDer()
time.sleep(1.2)

Omni.Stop()
time.sleep(0.5)

Omni.GiroIzq()
time.sleep(0.3)

Omni.Stop()
time.sleep(0.5)

Omni.Izquierda()
time.sleep(1)
Omni.Stop()