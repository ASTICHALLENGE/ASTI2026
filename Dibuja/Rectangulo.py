import time

import sys
sys.path.append('/home/asti/CodigosRobot')
import Omni

Omni.setVelocidad(130)

Omni.Avanza()
time.sleep(1)

Omni.Derecha()
time.sleep(2)

Omni.Atras()
time.sleep(1)

Omni.Izquierda()
time.sleep(2)