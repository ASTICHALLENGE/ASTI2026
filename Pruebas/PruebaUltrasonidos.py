from pymata4 import pymata4
import time

board = pymata4.Pymata4()

# Sensor 1 (Adelante)
trig1, echo1 = 22, 23
# Sensor 2 (Derecha)
trig2, echo2 = 24, 25
# Sensor 3 (Izquierda)
trig3, echo3 = 26, 27
# Sensor 4 (Atras)
trig4, echo4 = 28, 29

# Diccionario para traducir el n�mero de pin al nombre del sensor
nombres_sensores = {
    trig1: "Adelante",
    trig2: "Derecha",
    trig3: "Izquierda",
    trig4: "Atras"
}

def leerUS(data):
    # data[1] contiene el pin Trigger
    # data[2] contiene la distancia en cm
    pin_trigger = data[1]
    distancia = data[2]
    
    # Buscamos el nombre del sensor segun su pin
    nombre = nombres_sensores.get(pin_trigger, "Desconocido")
    
    print(f"Sensor {nombre}: {distancia} cm")

board.set_pin_mode_sonar(trig1, echo1, leerUS)
board.set_pin_mode_sonar(trig2, echo2, leerUS)
board.set_pin_mode_sonar(trig3, echo3, leerUS)
board.set_pin_mode_sonar(trig4, echo4, leerUS)

print("�Sensores listos! Leyendo distancias...")

while True:
    time.sleep(0.1)
