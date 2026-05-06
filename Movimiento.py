from pymata4 import pymata4

board = pymata4.Pymata4()

mot1A = 4
mot1R = 3
mot2A = 6
mot2R = 5

enA = 2
enB = 7

#Set Up
board.set_pin_mode_pwm_output(enA)
board.set_pin_mode_pwm_output(enB)

board.set_pin_mode_digital_output(mot1A)
board.set_pin_mode_digital_output(mot1R)
board.set_pin_mode_digital_output(mot2A)
board.set_pin_mode_digital_output(mot2R)

def Avanza():
    board.digital_write(mot1A, 1)
    board.digital_write(mot1R, 0)

    board.digital_write(mot2A, 1)
    board.digital_write(mot2R, 0)

def Atras():
    board.digital_write(mot1A, 0)
    board.digital_write(mot1R, 1)

    board.digital_write(mot2A, 0)
    board.digital_write(mot2R, 1)

def Derecha():
    board.digital_write(mot1A, 1)
    board.digital_write(mot1R, 0)

    board.digital_write(mot2A, 0)
    board.digital_write(mot2R, 1)

def Izquierda():
    board.digital_write(mot1A, 0)
    board.digital_write(mot1R, 1)

    board.digital_write(mot2A, 1)
    board.digital_write(mot2R, 0)

def AvanzaDer():
    board.digital_write(mot1A, 1)
    board.digital_write(mot1R, 0)

    board.digital_write(mot2A, 0)
    board.digital_write(mot2R, 0)

def AvanzaIzq():
    board.digital_write(mot1A, 0)
    board.digital_write(mot1R, 0)

    board.digital_write(mot2A, 1)
    board.digital_write(mot2R, 0)

def AtrasDer():
    board.digital_write(mot1A, 0)
    board.digital_write(mot1R, 1)

    board.digital_write(mot2A, 0)
    board.digital_write(mot2R, 0)

def AtrasIzq():
    board.digital_write(mot1A, 0)
    board.digital_write(mot1R, 0)

    board.digital_write(mot2A, 0)
    board.digital_write(mot2R, 1)

def Stop():
    board.digital_write(mot1A, 0)
    board.digital_write(mot1R, 0)

    board.digital_write(mot2A, 0)
    board.digital_write(mot2R, 0)

def setVelocidad(velocidad):
    vel = velocidad
    if(velocidad>255):
        board.pwm_write(enA, 255)
        board.pwm_write(enB, 255)
    elif(velocidad<0):
        board.pwm_write(enA, 0)
        board.pwm_write(enB, 0)
    else:
        board.pwm_write(enA, vel)
        board.pwm_write(enB, vel)

