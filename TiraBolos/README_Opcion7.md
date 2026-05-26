# 🎳 TiraBolos - Detección de Bolos con YOLOv8 (Opcion7)

## 📋 Descripción

`Opcion7_Python313.py` es un sistema de detección y seguimiento de bolos de bowling para robots autónomos. Utiliza **Ultralytics YOLOv8** para realizar inferencia local de visión por computadora, permitiendo que el robot detecte bolos en tiempo real y navegue hacia ellos de forma autónoma.

### ¿Por qué se creó esta versión?

Esta versión fue desarrollada para:
- ✅ **Compatibilidad con Python 3.13.5**: Versiones anteriores usaban librerías incompatibles
- ✅ **Inferencia local**: No requiere conexión a internet ni API keys de Roboflow
- ✅ **Mayor velocidad**: Procesamiento más rápido al ejecutarse localmente
- ✅ **Mayor privacidad**: Los datos de la cámara no salen del robot
- ✅ **Independencia**: Funciona sin depender de servicios externos

---

## 🔧 Requisitos

### Requisitos del Sistema
- **Python**: 3.13.5 (o superior)
- **Sistema Operativo**: Linux (probado en Raspberry Pi)
- **Hardware**:
  - Cámara USB compatible con OpenCV
  - Robot con módulo de movimiento (Arduino + motores)
  - Mínimo 2GB RAM recomendado

### Dependencias de Python
```bash
ultralytics>=8.0.0
opencv-contrib-python>=4.8.0
```

---

## 📦 Instalación

### Paso 1: Clonar el Repositorio
```bash
cd ~
git clone https://github.com/tu-usuario/ASTI2026.git
cd ASTI2026
```

### Paso 2: Instalar Dependencias
```bash
pip install ultralytics opencv-contrib-python
```

**Nota**: Si usas un entorno virtual, actívalo primero:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

### Paso 3: Verificar la Instalación
```bash
python -c "from ultralytics import YOLO; import cv2; print('✓ Instalación correcta')"
```

---

## 🤖 Configuración del Modelo

### Opción A: Usar tu Modelo Personalizado de Roboflow

#### 1. Exportar el Modelo desde Roboflow

1. Ve a tu proyecto en Roboflow: https://app.roboflow.com/
2. Navega a tu workspace y proyecto:
   - **Workspace**: `lsc-kik8c`
   - **Proyecto**: `bowling-pin-detection`
   - **Versión**: `3` (o la versión que desees)

3. Haz clic en **"Export"** (botón azul en la esquina superior derecha)

4. Selecciona el formato de exportación:
   - **Format**: `YOLOv8`
   - **Show download code**: Desactiva esta opción
   - Haz clic en **"Continue"**

5. Descarga el archivo `.zip`

#### 2. Extraer y Ubicar el Modelo

```bash
# Descomprimir el archivo descargado
unzip bowling-pin-detection-3.zip -d ~/Downloads/bowling-model

# Crear la carpeta de modelos en el proyecto
mkdir -p ~/ASTI2026/TiraBolos/models

# Buscar el archivo del modelo (puede estar en diferentes ubicaciones)
# Opción 1: En la raíz
cp ~/Downloads/bowling-model/best.pt ~/ASTI2026/TiraBolos/models/bowling_pin_yolov8.pt

# Opción 2: En carpeta weights
cp ~/Downloads/bowling-model/weights/best.pt ~/ASTI2026/TiraBolos/models/bowling_pin_yolov8.pt
```

#### 3. Verificar la Ubicación del Modelo

```bash
ls -lh ~/ASTI2026/TiraBolos/models/bowling_pin_yolov8.pt
```

Deberías ver algo como:
```
-rw-r--r-- 1 usuario usuario 6.2M may 26 14:30 bowling_pin_yolov8.pt
```

### Opción B: Usar un Modelo Pre-entrenado de YOLOv8

Si no tienes un modelo personalizado, puedes usar un modelo pre-entrenado de YOLOv8:

```python
# Modificar la línea 73 en Opcion7_Python313.py:
MODEL_PATH = "yolov8n.pt"  # Modelo nano (más rápido, menos preciso)
# o
MODEL_PATH = "yolov8s.pt"  # Modelo small (balance)
# o
MODEL_PATH = "yolov8m.pt"  # Modelo medium (más preciso, más lento)
```

**Nota**: Los modelos pre-entrenados detectan objetos comunes (personas, coches, etc.) pero NO están entrenados específicamente para bolos de bowling. Para mejores resultados, usa tu modelo personalizado de Roboflow.

---

## 📁 Estructura de Archivos

```
ASTI2026/
├── TiraBolos/
│   ├── models/
│   │   └── bowling_pin_yolov8.pt    ← Archivo del modelo YOLOv8
│   ├── Opcion7_Python313.py          ← Script principal
│   ├── README_Opcion7.md             ← Este archivo
│   ├── Opcion5.py                    ← Versión anterior (Roboflow API)
│   └── ...
├── Movimiento.py                     ← Módulo de control de motores
└── requirements.txt
```

---

## 🚀 Uso

### Ejecución Básica

```bash
cd ~/ASTI2026
python TiraBolos/Opcion7_Python313.py
```

### Salir del Programa

Presiona la tecla **`q`** en la ventana de visualización para detener el robot y cerrar el programa.

### Modo Debug

El modo debug está activado por defecto (`DEBUG = True` en línea 114). Esto muestra:
- 📹 Ventana con la imagen de la cámara
- 🎯 Cajas delimitadoras alrededor de los bolos detectados
- 📊 FPS, número de bolos detectados y acción actual
- 📏 Líneas de división de zonas (izquierda, centro, derecha)

Para desactivar el modo debug:
```python
DEBUG = False  # Línea 114
```

---

## ⚙️ Parámetros Configurables

Todos los parámetros se encuentran en las líneas 94-114 del archivo:

### Velocidades del Robot
```python
VEL_NORMAL    = 130    # Velocidad de navegación normal
VEL_ATAQUE    = 180    # Velocidad máxima para sprint final
VEL_BUSQUEDA  = 110    # Velocidad de giro al buscar bolos
```

### Zonas de Detección (Frame de 640px de ancho)
```python
ZONA_IZQ      = 220    # Límite izquierdo (px)
ZONA_DER      = 420    # Límite derecho (px)
CENTRO_X      = 320    # Centro del frame (px)
```

**Visualización de zonas:**
```
|←  IZQ  →|← CENTRO →|←  DER  →|
0        220        420        640 (px)
```

### Umbral de Proximidad
```python
AREA_CERCA    = 8000   # Área mínima (px²) para activar sprint
```
- **Área pequeña** → Bolo lejos → Avanza normal
- **Área grande** → Bolo cerca → Sprint

### Confianza de Detección
```python
CONF_MIN      = 0.40   # Confianza mínima (0.0 - 1.0)
```
- Valores más altos (0.6-0.8): Menos falsos positivos, puede perder detecciones
- Valores más bajos (0.3-0.5): Más detecciones, más falsos positivos

### Modo Búsqueda
```python
MAX_SIN_BOLO  = 15     # Frames sin detección antes de buscar
```

---

## 🧠 Lógica de Detección

### Sistema de 3 Zonas

El frame de la cámara se divide en 3 zonas horizontales:

```
┌─────────────────────────────────────────┐
│         ZONA IZQUIERDA (< 220px)        │
│  ┌───────────────────────────────────┐  │
│  │    ZONA CENTRO (220-420px)        │  │
│  │                                   │  │
│  │         [BOLO DETECTADO]          │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│         ZONA DERECHA (> 420px)          │
└─────────────────────────────────────────┘
```

### Árbol de Decisión

```
¿Bolo detectado?
├─ NO → Incrementar contador
│       ├─ Contador < 15 → STOP (esperar)
│       └─ Contador ≥ 15 → BUSCAR (girar lento)
│
└─ SÍ → Resetear contador
        ├─ Área ≥ 8000 px² → SPRINT (velocidad máxima)
        ├─ Centro X < 220  → IZQUIERDA (girar)
        ├─ Centro X > 420  → DERECHA (girar)
        └─ 220 ≤ X ≤ 420   → AVANZA (velocidad normal)
```

---

## 🏃 Modos de Movimiento

### 1. 🔍 Modo BÚSQUEDA
**Activación**: No se detectan bolos durante 15 frames consecutivos

**Comportamiento**:
- Gira lentamente (velocidad: `VEL_BUSQUEDA = 110`)
- Dirección de giro basada en última detección
- Continúa hasta detectar un bolo

**Código relevante** (líneas 317-325):
```python
if frames_sin_bolo >= MAX_SIN_BOLO:
    mov.setVelocidad(VEL_BUSQUEDA)
    if dir_busqueda > 0:
        mov.Derecha()
    else:
        mov.Izquierda()
```

### 2. 🎯 Modo APROXIMACIÓN
**Activación**: Bolo detectado pero área < 8000 px²

**Comportamiento**:
- **Bolo a la izquierda** (X < 220): Gira a la izquierda
- **Bolo a la derecha** (X > 420): Gira a la derecha
- **Bolo centrado** (220 ≤ X ≤ 420): Avanza recto
- Velocidad: `VEL_NORMAL = 130`

**Código relevante** (líneas 276-294):
```python
if cx < ZONA_IZQ:
    accion = "IZQUIERDA"
elif cx > ZONA_DER:
    accion = "DERECHA"
else:
    accion = "AVANZA"
```

### 3. 🚀 Modo SPRINT
**Activación**: Bolo detectado con área ≥ 8000 px²

**Comportamiento**:
- Avanza a máxima velocidad hacia el bolo
- Velocidad: `VEL_ATAQUE = 180`
- No realiza correcciones de dirección (asume que está alineado)

**Código relevante** (líneas 270-274):
```python
if area >= AREA_CERCA:
    accion = "AVANZA"
    vel    = VEL_ATAQUE
    label  = f"SPRINT  area={int(area)}"
```

---

## 🔧 Solución de Problemas

### ❌ Error: "No se encuentra el archivo del modelo"

**Síntoma**:
```
ERROR: No se encuentra el archivo del modelo
Ruta buscada: /home/asti/ASTI2026/TiraBolos/models/bowling_pin_yolov8.pt
```

**Soluciones**:
1. Verifica que el archivo existe:
   ```bash
   ls -lh TiraBolos/models/bowling_pin_yolov8.pt
   ```

2. Si no existe, descarga y coloca el modelo (ver sección "Configuración del Modelo")

3. Verifica los permisos del archivo:
   ```bash
   chmod 644 TiraBolos/models/bowling_pin_yolov8.pt
   ```

### ❌ Error: "No se encuentra el módulo 'ultralytics'"

**Síntoma**:
```
ERROR: No se encuentra el módulo 'ultralytics'
```

**Solución**:
```bash
pip install ultralytics
# o si usas pip3:
pip3 install ultralytics
```

### ❌ Error: "Error al conectar la cámara"

**Síntoma**:
```
Error al conectar la cámara
```

**Soluciones**:
1. Verifica que la cámara está conectada:
   ```bash
   ls /dev/video*
   ```

2. Prueba con otro índice de cámara (línea 130):
   ```python
   cam = cv2.VideoCapture(1)  # Prueba con 1, 2, etc.
   ```

3. Verifica permisos:
   ```bash
   sudo usermod -a -G video $USER
   # Luego reinicia la sesión
   ```

### ❌ El robot no se mueve

**Posibles causas**:
1. **Módulo Movimiento no encontrado**: Verifica que `Movimiento.py` existe en `/home/asti/CodigosRobot`
2. **Arduino no conectado**: Verifica la conexión USB del Arduino
3. **Velocidad muy baja**: Aumenta los valores de velocidad (líneas 95-97)

**Solución**:
```bash
# Verificar módulo
ls /home/asti/CodigosRobot/Movimiento.py

# Verificar Arduino
ls /dev/ttyUSB* /dev/ttyACM*
```

### 🐌 FPS muy bajo (< 5 FPS)

**Causas**:
- Modelo muy grande para el hardware
- Resolución de cámara muy alta

**Soluciones**:
1. Usar un modelo más pequeño:
   ```python
   MODEL_PATH = "yolov8n.pt"  # Modelo nano (más rápido)
   ```

2. Reducir resolución de cámara (líneas 131-132):
   ```python
   cam.set(cv2.CAP_PROP_FRAME_WIDTH,  320)  # En lugar de 640
   cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # En lugar de 480
   ```

3. Desactivar modo debug:
   ```python
   DEBUG = False
   ```

### 🎯 Detecciones imprecisas o falsos positivos

**Soluciones**:
1. Aumentar confianza mínima (línea 109):
   ```python
   CONF_MIN = 0.60  # En lugar de 0.40
   ```

2. Reentrenar el modelo con más imágenes en Roboflow

3. Mejorar iluminación del entorno

---

## 🔄 Diferencias con Opcion5.py

| Característica | Opcion5.py (Roboflow API) | Opcion7.py (YOLOv8 Local) |
|----------------|---------------------------|---------------------------|
| **Inferencia** | Nube (Roboflow API) | Local (Ultralytics) |
| **Conexión Internet** | ✅ Requerida | ❌ No requerida |
| **API Key** | ✅ Requerida | ❌ No requerida |
| **Velocidad** | ~5-10 FPS (depende de red) | ~15-30 FPS (depende de hardware) |
| **Privacidad** | Datos enviados a Roboflow | Datos permanecen locales |
| **Python** | 3.7 - 3.11 | 3.13.5+ |
| **Dependencias** | `inference-sdk` | `ultralytics` |
| **Formato Modelo** | API de Roboflow | Archivo `.pt` local |
| **Latencia** | Alta (red + procesamiento) | Baja (solo procesamiento) |
| **Costo** | Límite de llamadas API | Sin límites |

### Migración de Opcion5 a Opcion7

Si estás usando `Opcion5.py` y quieres migrar:

1. **Exporta tu modelo** desde Roboflow en formato YOLOv8
2. **Instala Ultralytics**: `pip install ultralytics`
3. **Coloca el modelo** en `TiraBolos/models/bowling_pin_yolov8.pt`
4. **Ejecuta Opcion7**: `python TiraBolos/Opcion7_Python313.py`

**Ventajas de migrar**:
- ✅ Mayor velocidad (2-3x más rápido)
- ✅ Funciona sin internet
- ✅ Sin límites de API
- ✅ Compatible con Python 3.13+

---

## 📚 Recursos Adicionales

### Documentación Oficial
- **Ultralytics YOLOv8**: https://docs.ultralytics.com/
- **Roboflow**: https://docs.roboflow.com/
- **OpenCV Python**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html

### Tutoriales Recomendados
- [Entrenar YOLOv8 con Roboflow](https://blog.roboflow.com/how-to-train-yolov8-on-a-custom-dataset/)
- [Exportar modelos de Roboflow](https://docs.roboflow.com/exporting-data)
- [Optimizar YOLOv8 para Raspberry Pi](https://docs.ultralytics.com/guides/raspberry-pi/)

### Comunidad
- **Roboflow Universe**: https://universe.roboflow.com/
- **Ultralytics GitHub**: https://github.com/ultralytics/ultralytics
- **Foro de Ultralytics**: https://community.ultralytics.com/

---

## 🤝 Contribuciones

Si encuentras errores o tienes sugerencias de mejora:

1. Abre un issue en el repositorio
2. Propón cambios mediante pull request
3. Documenta cualquier modificación importante

---

## 📝 Notas Finales

### Ajustes Recomendados por Entorno

**Entorno con buena iluminación**:
```python
CONF_MIN = 0.50  # Confianza más alta
AREA_CERCA = 10000  # Sprint más cerca
```

**Entorno con poca luz**:
```python
CONF_MIN = 0.35  # Confianza más baja
VEL_NORMAL = 110  # Velocidad más conservadora
```

**Robot rápido/ágil**:
```python
VEL_ATAQUE = 200  # Sprint más agresivo
MAX_SIN_BOLO = 10  # Búsqueda más rápida
```

**Robot lento/pesado**:
```python
VEL_ATAQUE = 150  # Sprint más controlado
MAX_SIN_BOLO = 20  # Más paciencia antes de buscar
```

---

## 📄 Licencia

Este código es parte del proyecto ASTI2026 del Club de Robótica.

---

**Versión**: 7.0  
**Última actualización**: Mayo 2026  
**Autor**: Club de Robótica ASTI  
**Compatible con**: Python 3.13.5+, Ultralytics YOLOv8

---

🎳 **¡Buena suerte con tu robot tira-bolos!** 🤖