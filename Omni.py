from pymata4 import pymata4

board = pymata4.Pymata4()

# 11 --> Izquierda Arriba
# 12 --> Izquierda Abajo
# 21 --> Derecha Arriba
# 22 --> Derecha Abajo

mot11A = 4
mot11R = 4

mot12A = 3
mot12R = 3

mot21A = 6
mot21R = 6

mot22A = 5
mot22R = 5

en1A = 2
en1B = 7

en2A = 2
en2B = 7

#Set Up
board.set_pin_mode_pwm_output(en1A)
board.set_pin_mode_pwm_output(en1B)

board.set_pin_mode_pwm_output(en2A)
board.set_pin_mode_pwm_output(en2B)

board.set_pin_mode_digital_output(mot11A)
board.set_pin_mode_digital_output(mot11R)

board.set_pin_mode_digital_output(mot12A)
board.set_pin_mode_digital_output(mot12R)

board.set_pin_mode_digital_output(mot21A)
board.set_pin_mode_digital_output(mot21R)

board.set_pin_mode_digital_output(mot22A)
board.set_pin_mode_digital_output(mot22R)

def Avanza():
    board.digital_write(mot11A, 1)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 1)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 1)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 1)
    board.digital_write(mot22R, 0)

def Atras():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 1)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 1)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 1)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 1)

def Derecha():
    board.digital_write(mot11A, 1)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 1)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 1)

    board.digital_write(mot22A, 1)
    board.digital_write(mot22R, 0)

def Izquierda():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 1)
    
    board.digital_write(mot12A, 1)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 1)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 1)

def AvanzaDer():
    board.digital_write(mot11A, 1)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 1)
    board.digital_write(mot22R, 0)

def AvanzaIzq():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 1)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 1)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 0)

def AtrasDer():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 1)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 1)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 0)

def AtrasIzq():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 1)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 1)

def GiroDer():
    board.digital_write(mot11A, 1)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 1)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 1)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 1)

def GiroIzq():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 1)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 1)

    board.digital_write(mot21A, 1)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 1)
    board.digital_write(mot22R, 0)

def Stop():
    board.digital_write(mot11A, 0)
    board.digital_write(mot11R, 0)
    
    board.digital_write(mot12A, 0)
    board.digital_write(mot12R, 0)

    board.digital_write(mot21A, 0)
    board.digital_write(mot21R, 0)

    board.digital_write(mot22A, 0)
    board.digital_write(mot22R, 0)

def setVelocidad(velocidad):
    if(velocidad>255):
        board.pwm_write(en1A, 255)
        board.pwm_write(en1B, 255)

        board.pwm_write(en2A, 255)
        board.pwm_write(en2B, 255)
    elif(velocidad<0):
        board.pwm_write(en1A, 0)
        board.pwm_write(en1B, 0)

        board.pwm_write(en2A, 0)
        board.pwm_write(en2B, 0)
    else:
        board.pwm_write(en1A, velocidad)
        board.pwm_write(en1B, velocidad)

        board.pwm_write(en2A, velocidad)
        board.pwm_write(en2B, velocidad)

