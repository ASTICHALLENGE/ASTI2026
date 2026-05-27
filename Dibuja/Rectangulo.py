import time

import sys
sys.path.append('/home/asti/CodigosRobot')
import OmniAlrevez as Omni

Omni.setVelocidad(130)

Omni.Avanza()
time.sleep(0.5)

Omni.Derecha()
time.sleep(1.5)

Omni.Atras()
time.sleep(0.5)

Omni.Izquierda()
time.sleep(1.5)
Omni.Stop()