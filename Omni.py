from pymata4 import pymata4

# 11 --> Izquierda Arriba
# 12 --> Izquierda Abajo
# 21 --> Derecha Arriba
# 22 --> Derecha Abajo

mot11A = 3
mot11R = 2

mot12A = 4
mot12R = 5

mot21A = 8
mot21R = 9

mot22A = 6
mot22R = 7

vel=130

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
    board.pwm_write(mot11A, vel)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, vel)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel)
    board.pwm_write(mot22R, 0)

def Atras():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel)

def Derecha():
    board.pwm_write(mot11A, vel)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel)

    board.pwm_write(mot22A, vel)
    board.pwm_write(mot22R, 0)

def Izquierda():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel)
    
    board.pwm_write(mot12A, vel)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, vel)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel)

def AvanzaDer():
    board.pwm_write(mot11A, vel)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel)
    board.pwm_write(mot22R, 0)

def AvanzaIzq():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, vel)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, 0)

def AtrasDer():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, 0)

def AtrasIzq():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel)

def GiroDer():
    board.pwm_write(mot11A, vel)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel)

def GiroIzq():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel)

    board.pwm_write(mot21A, vel)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel)
    board.pwm_write(mot22R, 0)

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
    global vel
    if(velocidad>255):
        vel=255
    elif(velocidad<0):
        vel=0
    else:
        vel = velocidad

