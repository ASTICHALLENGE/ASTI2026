import time
import cv2
import sys
import base64
import requests

# Cargar tu m�dulo de movimiento
sys.path.append('/home/asti/CodigosRobot')
import Movimiento as mov

# 1. Credenciales y endpoint de Roboflow
API_KEY = "9i0t9PyAMW8L1fvghQ00" 
WORKSPACE = "jose-an"
WORKFLOW_ID = "general-segmentation-api"
URL = f"https://detect.roboflow.com/infer/workflows/{WORKSPACE}/{WORKFLOW_ID}"

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cam.isOpened():
    print("Error al conectar la c�mara")
    exit()

mov.setVelocidad(0)

while True:
    ret, frame = cam.read()
    if not ret:
        break

    try:
        t_inicio = time.time()
        
        # 2. Convertir la imagen a formato de texto (Base64) para el env�o HTTP
        _, buffer = cv2.imencode('.jpg', frame)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # 3. Estructurar la petici�n REST
        payload = {
            "api_key": API_KEY,
            "inputs": {
                "image": {
                    "type": "base64",
                    "value": img_b64
                },
                "classes": "bowling-pins"
            }
        }
        
        # 4. Enviar la imagen a la nube
        respuesta = requests.post(URL, json=payload)
        
        if respuesta.status_code != 200:
            print(f"Error HTTP: {respuesta.status_code} - {respuesta.text}")
            continue
            
        resultado = respuesta.json()
        
        # Imprimir FPS reales para monitorizar el retardo de la conexi�n
        fps = 1.0 / (time.time() - t_inicio)
        print(f"FPS (Nube API REST): {fps:.2f}", end="\r")

        # 5. Extraer las predicciones del JSON devuelto
        # Extraemos la lista dependiendo de c�mo la devuelva tu workflow espec�fico
        outputs = resultado.get("outputs", resultado) if isinstance(resultado, dict) else resultado
        
        predicciones = []
        for out in outputs:
            if "predictions" in out: 
                predicciones = out["predictions"]
            elif "model_predictions" in out: 
                predicciones = out["model_predictions"]

        # Buscar el bolo m�s grande (el que est� m�s cerca del robot)
        mejor_bolo = None
        mayor_area = 0

        for p in predicciones:
            if 'width' in p and 'height' in p:
                area = p['width'] * p['height']
                if area > mayor_area:
                    mayor_area = area
                    mejor_bolo = p

        # 6. L�gica de movimiento en 3 zonas
        if mejor_bolo:
            centro_x = int(mejor_bolo['x'])
            centro_y = int(mejor_bolo['y'])
            
            cv2.circle(frame, (centro_x, centro_y), 5, (0, 0, 255), -1)

            if centro_x < 256:
                mov.Izquierda()
            elif centro_x > 384:
                mov.Derecha()
            else:
                mov.Avanza()
        else:
            mov.Stop()

    except Exception as e:
        print(f"\nError durante la inferencia: {e}")
        mov.Stop()

    cv2.imshow("Camara - Roboflow REST API", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
mov.Stop()