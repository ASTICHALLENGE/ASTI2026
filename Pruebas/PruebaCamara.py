import cv2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cam.isOpened():
    print("Error al conectar la camara")
    exit()

while True:
    ret1, frame = cam.read() # Tomo la foto
    cv2.imshow("contornos", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): # Para que cuando le de a la 'q' pare 
        break

cam.release() #Para dejar de usar la camara
cv2.destroyAllWindows() #Para cerrar las pestanas