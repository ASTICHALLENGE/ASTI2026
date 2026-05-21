from pymata4 import pymata4
import time

import sys
sys.path.append('/home/asti/CodigosRobot')
import Omni

board = pymata4.Pymata4()

# Pines y variables
trig1, echo1 = 22, 23
trig2, echo2 = 24, 25
trig3, echo3 = 26, 27
trig4, echo4 = 28, 29

busqueda = 0

# 1. Creamos nuestro "Panel de Control" global
distAct = {
    "Adelante": 0,
    "Derecha": 0,
    "Izquierda": 0,
    "Atras": 0
}

# Diccionario para saber que pin corresponde a que sensor
nombres_sensores = {
    trig1: "Adelante",
    trig2: "Derecha",
    trig3: "Izquierda",
    trig4: "Atras"
}

# 2. El Callback: Solo actualiza el panel de control
def leerUS(data):
    pin_trigger = data[1]
    distancia = data[2]
    
    # Obtenemos el nombre del sensor (Adelante, Derecha...)
    nombre = nombres_sensores.get(pin_trigger)
    if nombre:
        # Actualizamos el valor en nuestro diccionario global
        distAct[nombre] = distancia

# 3. Inicializamos los sensores
print("Encendiendo sensores...")
board.set_pin_mode_sonar(trig1, echo1, leerUS)
board.set_pin_mode_sonar(trig2, echo2, leerUS)
board.set_pin_mode_sonar(trig3, echo3, leerUS)
board.set_pin_mode_sonar(trig4, echo4, leerUS)
time.sleep(0.5) # Damos tiempo para que se estabilicen las primeras lecturas

#Giro del principio
Omni.GiroDer()
time.sleep(1)

# 4. Bucle principal
try:
    while True:
        # leo valor del diccionario
        dist1 = distAct["Adelante"]
        dist2 = distAct["Derecha"]
        dist3 = distAct["Izquierda"]
        dist4 = distAct["Atras"]
        
        if dist1>0 and dist1<20:
            Omni.Avanza() 
            busqueda=0

        elif dist2>0 and dist2<20:
            Omni.Derecha()
            busqueda=0

        elif dist3>0 and dist3<20:
            Omni.Izquierda()
            busqueda=0

        elif dist4>0 and dist4<20:
            Omni.Atras()
            busqueda=0

        elif busqueda>30:
            Omni.AtrasIzq()
            busqueda+=1
            if busqueda>40: busqueda=0

        elif busqueda>20:
            Omni.AtrasDer()
            busqueda+=1

        elif busqueda>10:
            Omni.AvanzaDer()
            busqueda+=1

        else:
            Omni.AvanzaIzq()
            busqueda+=1


        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nDeteniendo programa...")
finally:
    board.shutdown()