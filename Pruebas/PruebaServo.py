from pymata4 import pymata4
import time

# Usaremos el pin 9 para este ejemplo
servo1 = 20
servo2 = 23

# 180 --> der
# 20 --> izq 


print("Conectando con el Arduino Mega...")
board = pymata4.Pymata4()

try:
    print("Iniciando servo...")
    # 1. Configuramos el pin como salida de servo
    board.set_pin_mode_servo(servo1)
    board.set_pin_mode_servo(servo2)
    time.sleep(1) # Le damos un segundo para estabilizarse
    
    print("Movimiento de prueba iniciado.")
    
    while True:

        board.servo_write(servo1, 90)
        board.servo_write(servo2, 0)

except KeyboardInterrupt:
    print("\nDeteniendo y apagando...")
finally:
    board.shutdown()