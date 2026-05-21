import time

import sys
sys.path.append('/home/asti/CodigosRobot')
import Omni

Omni.setVelocidad(130)

Omni.AvanzaDer()
time.sleep(1.75)

Omni.AtrasDer()
time.sleep(1.75)

Omni.Izquierda()
time.sleep(1.75)
Omni.Stop()