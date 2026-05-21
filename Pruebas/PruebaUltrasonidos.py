from pymata4 import pymata4
import time

board = pymata4.Pymata4()

# 1 --> adelante
# 2 --> derecha
# 3 --> izquierda
# 4 --> atras

trig1 = 20
echo1 = 21

trig2 = 22
echo2 = 23

trig3 = 24
echo3 = 25

trig4 = 26
echo4 = 27


def leerUS(data):
    distancia = data[2]
    print(f"Distancia")

board.set_pin_mode_sonar(trig1, echo1, leerUS)

while True:
    time.sleep(0.1)

