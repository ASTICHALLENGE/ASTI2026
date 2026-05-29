from pymata4 import pymata4

# 11 --> Izquierda Arriba
# 12 --> Izquierda Abajo
# 21 --> Derecha Arriba
# 22 --> Derecha Abajo

mot11A = 5
mot11R = 4

mot12A = 2
mot12R = 3

mot21A = 6
mot21R = 7

mot22A = 8
mot22R = 9

vel1=130
vel2=130

board = None

#Set Up
def init_motores(placa_principal):
    global board
    board = placa_principal  # Enlazamos con la conexi�n del c�digo principal

    board.set_pin_mode_pwm_output(mot11A)
    board.set_pin_mode_pwm_output(mot11R)
    board.set_pin_mode_pwm_output(mot12A)
    board.set_pin_mode_pwm_output(mot12R)
    board.set_pin_mode_pwm_output(mot21A)
    board.set_pin_mode_pwm_output(mot21R)
    board.set_pin_mode_pwm_output(mot22A)
    board.set_pin_mode_pwm_output(mot22R)

def Avanza():
    board.pwm_write(mot11A, vel1)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel1)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, vel2)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel2)
    board.pwm_write(mot22R, 0)

def Atras():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel1)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel1)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel2)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel2)

def Derecha():
    board.pwm_write(mot11A, vel1)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel1)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel2)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel2)

def Izquierda():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel1)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel1)

    board.pwm_write(mot21A, vel2)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel2)
    board.pwm_write(mot22R, 0)

def AvanzaDer():
    board.pwm_write(mot11A, vel1)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel1)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, 0)

def AvanzaIzq():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, vel2)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel2)
    board.pwm_write(mot22R, 0)

def AtrasDer():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel1)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel1)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, 0)

def AtrasIzq():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel2)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel2)

def Stop():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, 0)

def setVelocidad(velocidad):
    global vel1
    global vel2
    if(velocidad>255):
        vel1=255
        vel2=255
    elif(velocidad<0):
        vel1=0
        vel2=0
    else:
        vel1 = velocidad
        vel2 = velocidad

def setVelocidades(vel_izq, vel_der):
    """Control independiente de cada lado para seguimiento proporcional."""
    # Lado izquierdo (motores 11 y 12)
    board.pwm_write(mot11A, vel_izq)
    board.pwm_write(mot11R, 0)
    board.pwm_write(mot12A, vel_izq)
    board.pwm_write(mot12R, 0)
    # Lado derecho (motores 21 y 22)
    board.pwm_write(mot21A, vel_der)
    board.pwm_write(mot21R, 0)
    board.pwm_write(mot22A, vel_der)
    board.pwm_write(mot22R, 0)


