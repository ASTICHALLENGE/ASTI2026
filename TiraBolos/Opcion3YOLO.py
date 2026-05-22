import time
import cv2
import sys
from inference_sdk import InferenceHTTPClient

# Cargar tu módulo de movimiento
sys.path.append('/home/asti/CodigosRobot')
import Movimiento as mov

# 1. Conexión a tu Workspace en la nube
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=""#Meter api key
)

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cam.isOpened():
    print("Error al conectar la cámara")
    exit()

mov.setVelocidad(130)

while True:
    ret, frame = cam.read()
    if not ret:
        break

    # 2. Inferencia en la nube
    # Pasamos la variable 'frame' (numpy array) directamente en lugar de "YOUR_IMAGE.jpg"
    try:
        t_inicio = time.time()
        
        result = client.run_workflow(
            workspace_name="jose-an",
            workflow_id="general-segmentation-api",
            images={
                "image": frame  
            },
            parameters={
                "classes": "bowling-pins"
            },
            use_cache=False # Crucial ponerlo en False para vídeo en directo
        )
        
        # Mostramos los FPS reales para ver el retraso de la red
        fps = 1.0 / (time.time() - t_inicio)
        print(f"FPS (Nube): {fps:.2f}", end="\r")

        # 3. Analizar la respuesta JSON de Roboflow
        # El formato exacto de 'result' depende de los bloques de tu workflow.
        # Generalmente, las detecciones vienen en una lista dentro de una clave.
        predicciones = []
        for output in result:
            # Buscamos la lista de predicciones. 
            # (Si esto falla, añade un print(result) para ver el nombre exacto de la clave)
            if "predictions" in output: 
                predicciones = output["predictions"]
            elif "model_predictions" in output: # Otro nombre común en Roboflow
                predicciones = output["model_predictions"]

        # Buscar el bolo más grande (el más cercano)
        mejor_bolo = None
        mayor_area = 0

        for p in predicciones:
            # Las coordenadas suelen venir con el centro (x, y) y las dimensiones (width, height)
            if 'width' in p and 'height' in p:
                area = p['width'] * p['height']
                if area > mayor_area:
                    mayor_area = area
                    mejor_bolo = p

        # 4. Lógica de movimiento (3 zonas)
        if mejor_bolo:
            centro_x = int(mejor_bolo['x'])
            centro_y = int(mejor_bolo['y'])
            
            # Dibujar un círculo rojo en la cámara
            cv2.circle(frame, (centro_x, centro_y), 5, (0, 0, 255), -1)

            if centro_x < 256:
                mov.Izquierda()
                # print("Girando a la izquierda")
            elif centro_x > 384:
                mov.Derecha()
                # print("Girando a la derecha")
            else:
                mov.Avanza()
                # print("¡Ataque frontal!")
        else:
            mov.Stop()

    except Exception as e:
        print(f"\nError de conexión: {e}")
        mov.Stop()

    cv2.imshow("Camara - Roboflow API", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
mov.Stop()