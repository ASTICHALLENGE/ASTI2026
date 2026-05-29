from pymata4 import pymata4

board = pymata4.Pymata4()

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

vel = 130

board.set_pin_mode_pwm_output(mot11A)
board.set_pin_mode_pwm_output(mot11R)

board.set_pin_mode_pwm_output(mot12A)
board.set_pin_mode_pwm_output(mot12R)

board.set_pin_mode_pwm_output(mot21A)
board.set_pin_mode_pwm_output(mot21R)

board.set_pin_mode_pwm_output(mot22A)
board.set_pin_mode_pwm_output(mot22R)
try:
    while True:
        board.pwm_write(mot11A, vel)
        board.pwm_write(mot11R, 0)

except KeyboardInterrupt:
    board.pwm_write(mot11A, 0)
    board.pwm_write(mot11R, 0)
    
    board.pwm_write(mot12A, 0)
    board.pwm_write(mot12R, 0)

    board.pwm_write(mot21A, 0)
    board.pwm_write(mot21R, 0)

    board.pwm_write(mot22A, 0)
    board.pwm_write(mot22R, 0)   