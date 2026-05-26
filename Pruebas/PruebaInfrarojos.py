from pymata4 import pymata4
import time

board = pymata4.Pymata4()

# Sensor 1 (Adelante)
ir1 = 50
# Sensor 2 (Derecha)
ir2 = 14
# Sensor 3 (Izquierda)
ir3 = 52
# Sensor 4 (Atras)
ir4 = 53

blanco = 0
negro = 1
color = "blanco"

nombres_sensores = {
    ir1: "Adelante",
    ir2: "Derecha",
    ir3: "Izquierda",
    ir4: "Atras"
}

def leerIR(data):
    pin = data[1]
    valor = data[2]
    nombre = nombres_sensores.get(pin, "Desconocido")
    if valor==blanco: print(f"{nombre}: Blanco")
    elif valor==negro: print(f"{nombre}: Negro")

board.set_pin_mode_digital_input(ir1, callback=leerIR)
board.set_pin_mode_digital_input(ir2, callback=leerIR)
board.set_pin_mode_digital_input(ir3, callback=leerIR)
board.set_pin_mode_digital_input(ir4, callback=leerIR)

while True:
    time.sleep(0.1)