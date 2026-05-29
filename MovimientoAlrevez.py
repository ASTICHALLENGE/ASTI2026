from pymata4 import pymata4

# 11 --> Izquierda Arriba
# 12 --> Izquierda Abajo
# 21 --> Derecha Arriba
# 22 --> Derecha Abajo

mot11A = 9
mot11R = 8

mot12A = 7
mot12R = 6

mot21A = 3
mot21R = 2

mot22A = 4
mot22R = 5

vel=130
vel1 = vel
vel2 = vel
vel3 = vel
vel4 = vel

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
    
    board.pwm_write(mot12A, vel2)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, vel3)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel4)
    board.pwm_write(mot22R, 0)

def Atras():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel1)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel2)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel3)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel4)

def Derecha():
    board.pwm_write(mot11A, vel1)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel2)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, vel3)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel4)

def Izquierda():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel1)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel2)

    board.pwm_write(mot21A, vel3)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel4)
    board.pwm_write(mot22R, 0)

def AvanzaDer():
    board.pwm_write(mot11A, vel1)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, vel2)
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

    board.pwm_write(mot21A, vel3)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, vel4)
    board.pwm_write(mot22R, 0)

def AtrasDer():
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, vel1)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, vel2)

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
    board.pwm_write(mot21R, vel3)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, vel4)

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



def setVelocidad(motor, velocidad):
    match motor:
        case 1: # Izquierda arriba
            global vel1
            if(velocidad>255):
                vel1=255
            elif(velocidad<0):
                vel1=0
            else:
                vel1 = velocidad
        case 2: # Izquierda abajo
            global vel2
            if(velocidad>255):
                vel2=255
            elif(velocidad<0):
                vel2=0
            else:
                vel2 = velocidad
        case 3: # Derecha arriba
            global vel3
            if(velocidad>255):
                vel3=255
            elif(velocidad<0):
                vel3=0
            else:
                vel3 = velocidad
        case 4: # Derecha abajo
            global vel4
            if(velocidad>255):
                vel4=255
            elif(velocidad<0):
                vel4=0
            else:
                vel4 = velocidad

