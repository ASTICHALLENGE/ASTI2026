from pymata4 import pymata4
import time

import sys
sys.path.append('/home/asti/CodigosRobot')
import Omni

board = pymata4.Pymata4()

# Pines y variables
trig1, echo1 = 22, 23 # Sensor 1 (Adelante)
trig2, echo2 = 24, 25 # Sensor 2 (Derecha)
trig3, echo3 = 26, 27 # Sensor 3 (Izquierda)
trig4, echo4 = 28, 29 # Sensor 4 (Atras)

ir1 = 30 # Sensor 1 (Adelante)
ir2 = 31 # Sensor 2 (Derecha)
ir3 = 32 # Sensor 3 (Izquierda)
ir4 = 33 # Sensor 4 (Atras)

blanco = 0
negro = 1
busqueda = 0
cambioBusqueda = 10

# 1. Creamos nuestro "Panel de Control" global
distAct = {
    "Adelante": 0,
    "Derecha": 0,
    "Izquierda": 0,
    "Atras": 0
}
colorAct = {
    "Adelante": blanco,
    "Derecha": blanco,
    "Izquierda": blanco,
    "Atras": blanco
}

# Diccionario para saber que pin corresponde a que sensor
nombres_sensoresUS = {
    trig1: "Adelante",
    trig2: "Derecha",
    trig3: "Izquierda",
    trig4: "Atras"
}

nombres_sensoresIR = {
    ir1: "Adelante",
    ir2: "Derecha",
    ir3: "Izquierda",
    ir4: "Atras"
}

# 2. El Callback: Solo actualiza el panel de control
def leerUS(data):
    pin_trigger = data[1]
    distancia = data[2]
    
    # Obtenemos el nombre del sensor (Adelante, Derecha...)
    nombre = nombres_sensoresUS.get(pin_trigger)
    if nombre:
        # Actualizamos el valor en nuestro diccionario global
        distAct[nombre] = distancia

def leerIR(data):
    pinIR = data[1]
    valor = data[2]

    nombre = nombres_sensoresIR.get(pinIR)
    if nombre:
        if valor == blanco:
            colorAct[nombre] = blanco
        elif valor == negro:
            colorAct[nombre] = negro


# 3. Inicializamos los sensores
print("Encendiendo sensores...")
board.set_pin_mode_sonar(trig1, echo1, leerUS)
board.set_pin_mode_sonar(trig2, echo2, leerUS)
board.set_pin_mode_sonar(trig3, echo3, leerUS)
board.set_pin_mode_sonar(trig4, echo4, leerUS)

board.set_pin_mode_digital_input(ir1, callback=leerIR)
board.set_pin_mode_digital_input(ir2, callback=leerIR)
board.set_pin_mode_digital_input(ir3, callback=leerIR)
board.set_pin_mode_digital_input(ir4, callback=leerIR)
time.sleep(0.5) # Damos tiempo para que se estabilicen las primeras lecturas

#Giro del principio
Omni.GiroDer()
time.sleep(1)

# 4. Bucle principal
try:
    while True:
        col1 = colorAct["Adelante"]
        col2 = colorAct["Derecha"]
        col3 = colorAct["Izquierda"]
        col4 = colorAct["Atras"]

        if col1 == negro or col2 == negro or col3 == negro or col4 == negro:
            
            if col1 == negro:
                if col2 == negro:
                    Omni.AtrasIzq()
                elif col3 == negro:
                    Omni.AtrasDer()
                else:
                    Omni.Atras()
            elif col4 == negro:
                if col2 == negro:
                    Omni.AvanzaIzq()
                elif col3 == negro:
                    Omni.AvanzaDer()
                else:
                    Omni.Avanza()
            elif col2 == negro:
                Omni.Izquierda()
            elif col3 == negro:
                Omni.Derecha()
            busqueda+=1
        else:
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

            elif busqueda>cambioBusqueda*3:
                Omni.AtrasIzq()
                busqueda+=1
                if busqueda>cambioBusqueda*4: busqueda=0

            elif busqueda>cambioBusqueda*2:
                Omni.AtrasDer()
                busqueda+=1

            elif busqueda>cambioBusqueda:
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