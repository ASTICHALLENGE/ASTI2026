from pymata4 import pymata4
import time

import sys
sys.path.append('/home/asti/CodigosRobot')
import Omni

board = pymata4.Pymata4()

# Pines y variables
# Sensor 1 (Adelante)
trig1, echo1 = 49, 48
# Sensor 2 (Derecha)
trig2, echo2 = 43, 42
# Sensor 3 (Izquierda)
trig3, echo3 = 47, 46
# Sensor 4 (Atras)
trig4, echo4 = 45, 44

# Sensor 1 (Adelante)
ir1 = 50
# Sensor 2 (Derecha)
ir2 = 14
# Sensor 3 (Izquierda)
ir3 = 16
# Sensor 4 (Atras)
ir4 = 53

blanco = 0
negro = 1
busqueda = 0
cambioBusqueda = 10
distBusqueda = 30

Omni.init_motores(board)

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
    print(f"Sensor {nombre}: {distancia} cm")

def leerIR(data):
    pinIR = data[1]
    valor = data[2]

    nombre = nombres_sensoresIR.get(pinIR)
    if nombre:
        if valor == blanco:
            colorAct[nombre] = blanco
        elif valor == negro:
            colorAct[nombre] = negro
        print(f"{nombre}: {valor}")


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
                    print("Negro Arriba derecha")
                elif col3 == negro:
                    Omni.AtrasDer()
                    print("Negro Arriba Izquierda")
                else:
                    Omni.Atras()
                    print("Negro adelante")
            elif col4 == negro:
                if col2 == negro:
                    Omni.AvanzaIzq()
                    print("Negro Atras derecha")
                elif col3 == negro:
                    Omni.AvanzaDer()
                    print("Negro atras izquierda")

                else:
                    Omni.Avanza()
                    print("Negro atras")
            elif col2 == negro:
                Omni.Izquierda()
                print("Negro derecha")
            elif col3 == negro:
                Omni.Derecha()
                print("Negro izquierda")
            busqueda+=1
        else:
            # leo valor del diccionario
            dist1 = distAct["Adelante"]
            dist2 = distAct["Derecha"]
            dist3 = distAct["Izquierda"]
            dist4 = distAct["Atras"]
            
            if dist1>0 and dist1<distBusqueda:
                Omni.Avanza() 
                print("Detecta de frente")
                busqueda=0

            elif dist2>0 and dist2<distBusqueda:
                Omni.Derecha()
                print("Detecta a la derecha")
                busqueda=0

            elif dist3>0 and dist3<distBusqueda:
                Omni.Izquierda()
                print("Detecta a la izquierda")
                busqueda=0

            elif dist4>0 and dist4<distBusqueda:
                Omni.Atras()
                print("Detect atras")
                busqueda=0

            elif busqueda>cambioBusqueda*3:
                Omni.AtrasIzq()
                print("Busqueda 4")
                busqueda+=1
                if busqueda>cambioBusqueda*4: busqueda=0

            elif busqueda>cambioBusqueda*2:
                Omni.AtrasDer()
                print("Busqueda 3")
                busqueda+=1

            elif busqueda>cambioBusqueda:
                Omni.AvanzaDer()
                print("Busqueda 2")
                busqueda+=1

            else:
                Omni.AvanzaIzq()
                print("Busqueda 1")
                busqueda+=1
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nDeteniendo programa...")
finally:
    Omni.Stop()
    board.shutdown()