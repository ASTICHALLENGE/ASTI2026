# 🤖 CodigosRobot

Código para robots móviles con Arduino + Raspberry Pi. El repositorio contiene tres módulos principales: **robot sumo autónomo**, **siguelíneas** y **control manual por mando**.

---

## 📁 Estructura del proyecto

```
CodigosRobot/
├── Movimiento.py              # Control de motores (robot diferencial, 2 motores)
├── Omni.py                    # Control de motores (robot omnidireccional, 4 motores)
├── requirements.txt           # Dependencias Python
│
├── Sumo/
│   ├── config.py              # Parámetros del robot (puertos, velocidades, umbrales)
│   ├── sumo_main.py           # Máquina de estados principal del combate
│   ├── lidar_module.py        # Gestión del YDLidar (detección de rival)
│   ├── vision_module.py       # Visión por cámara (detección de línea y rival)
│   └── calibrar_lidar.py     # Herramienta de calibración de las barras del LiDAR
│
├── Siguelineas/
│   ├── Intento1.py            # Siguelíneas básico (3 zonas)
│   └── Intento2.py            # Siguelíneas avanzado (ROI doble, giros 90°, intersecciones)
│
└── Mando/
    ├── Mando.py               # Control manual del robot diferencial con mando PS
    └── MandoOmni.py           # Control manual del robot omnidireccional con mando PS
```

---

## ⚙️ Hardware requerido

| Componente | Descripción |
|---|---|
| Raspberry Pi | Ejecuta todo el código Python |
| Arduino (+ Firmata) | Controla los pines PWM/digitales vía pymata4 |
| YDLidar | Escáner láser 360° para el robot sumo |
| Webcam USB | Visión por computador (siguelíneas y sumo) |
| Driver L298N (×2) | Puente H para motores DC |
| Mando PS (Bluetooth) | Control manual vía evdev |

---

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/CodigosRobot.git
cd CodigosRobot

# Instalar dependencias
pip install -r requirements.txt

# Instalar el SDK de YDLidar (solo para el módulo sumo)
pip install ydlidar
```

> **Nota:** El Arduino debe tener cargado el firmware **StandardFirmataPlus** para funcionar con pymata4.

---

## 🥊 Robot Sumo Autónomo (`Sumo/`)

### Funcionamiento

El robot implementa una **máquina de 5 estados** que combina LiDAR y cámara:

```
BÚSQUEDA → ORIENTAR → SEGUIR → ATAQUE
              ↑                    |
              └─── EVASIÓN ←───────┘  (prioridad absoluta al detectar el borde)
```

| Estado | Condición de activación | Acción |
|---|---|---|
| `BÚSQUEDA` | Sin rival detectado | Giro alternado barriendo 360° |
| `ORIENTAR` | Rival detectado, desalineado (>15°) | Gira hacia el rival |
| `SEGUIR` | Rival alineado, lejos | Avanza con corrección LiDAR + cámara |
| `ATAQUE` | Rival a menos de `LIDAR_ATTACK_DIST_MM` | Velocidad máxima |
| `EVASIÓN` | Borde de la lona detectado | Retrocede y gira (bloquea el bucle) |

### Ejecución

```bash
cd Sumo
python3 sumo_main.py
```

### Calibración del LiDAR

Antes del primer uso, calibra los ángulos de las barras del robot para que no interfieran con la detección:

```bash
cd Sumo
python3 calibrar_lidar.py
```

El script muestra en tiempo real qué ángulos detecta el LiDAR como objetos cercanos. Copia los rangos que aparecen siempre (las barras propias) en `OWN_BARS_ANGLE_EXCLUSIONS` dentro de `config.py`.

### Configuración principal (`Sumo/config.py`)

```python
LIDAR_PORT            = "/dev/ttyUSB0"   # Puerto del YDLidar
ARDUINO_PORT          = "/dev/ttyACM0"   # Puerto del Arduino
LIDAR_ATTACK_DIST_MM  = 350              # Distancia (mm) para pasar a ATAQUE
LIDAR_MAX_DIST_MM     = 1500             # Rango máximo de detección del rival
VEL_BUSQUEDA          = 160              # Velocidad de giro en búsqueda
VEL_ATAQUE            = 255              # Velocidad máxima en ataque
```

---

## 〰️ Siguelíneas (`Siguelineas/`)

Dos versiones disponibles, ambas usan la cámara USB.

### Intento1.py — versión básica

Divide el frame en 3 zonas (izquierda / centro / derecha) y dirige el robot hacia donde haya más píxeles negros (línea oscura sobre suelo claro).

```bash
python3 Siguelineas/Intento1.py
```

### Intento2.py — versión avanzada

Control proporcional con doble ROI (zona cercana + zona lejana) para mayor anticipación. Gestiona intersecciones, líneas paralelas y giros bruscos de 90°.

Características destacadas:
- Fusión ponderada de ROI cercano y lejano
- Detección automática de intersecciones
- Máquina de estados para giros de 90° (activación por N frames consecutivos)
- Recovery lateral (gira hacia el último lado conocido)

```bash
python3 Siguelineas/Intento2.py
```

---

## 🎮 Control manual por mando (`Mando/`)

Control del robot con un mando PlayStation conectado por Bluetooth.

| Acción | Control |
|---|---|
| Mover | Joystick izquierdo |
| Aumentar velocidad | R1 |
| Reducir velocidad | L1 |
| Avanzar / Retroceder con gatillo | R2 / L2 |
| Encender / Apagar | Botón PS (modo) |

```bash
# Robot diferencial
python3 Mando/Mando.py

# Robot omnidireccional
python3 Mando/MandoOmni.py
```

> El mando se conecta como `/dev/input/event5`. Si el número de evento es diferente, modifícalo en el script.

---

## 🔌 Pinout Arduino

### `Movimiento.py` (robot diferencial)

| Pin | Función |
|---|---|
| 2 | Enable A (PWM) |
| 7 | Enable B (PWM) |
| 3 | Motor 1 – Retroceso |
| 4 | Motor 1 – Avance |
| 5 | Motor 2 – Retroceso |
| 6 | Motor 2 – Avance |

### `Omni.py` (robot omnidireccional)

Cuatro motores organizados en dos puentes H. Ver comentarios en el archivo para el mapeo completo de pines.

---

## 📋 Dependencias

```
pyserial       # Comunicación serie con Arduino
pymata4        # Control de Arduino desde Python
numpy          # Operaciones matriciales (visión)
opencv-contrib-python  # Visión por computador
evdev          # Lectura del mando PlayStation
ydlidar        # SDK del escáner YDLidar (instalar aparte)
```
