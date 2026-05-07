import cv2
import numpy as np
import sys

sys.path.append('/home/asti/CodigosRobot')
import Movimiento

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
DEBUG        = True
CENTRO_X     = 320

# Velocidades
VEL_RECTA    = 135
VEL_CURVA    = 120
VEL_GIRO     = 120    # curvas suaves / rombos
VEL_90       = 120    # ← NUEVO: giros de 90° (el más lento)
VEL_RECOVERY = 115

# Control proporcional
KP           = 0.22
ZONA_MUERTA  = 55    # ← BAJADO de 70 a 28 (reacción más rápida)

# Umbrales de error
ERR_RECTA    = 40
ERR_CURVA    = 110
ERR_90       = 200   # ← NUEVO: error > 200px → modo giro brusco

# Contornos
AREA_MIN     = 700
AREA_MAX     = 140000
MAX_PERDIDO  = 30

# ROI doble
ROI_CERCA    = (320, 430)   # ← SUBIDA: ve la línea antes (era 360,460)
ROI_LEJOS    = (170, 290)   # ← SUBIDA en paralelo
PESO_LEJOS   = 0.50         # ← SUBIDO de 0.35 a 0.40 (más anticipación)

# Intersección
AREA_INTERSECCION = 4000
N_INTERSECCION    = 2

# Líneas paralelas
ANGULO_PARALELO  = 20
GROSOR_MIN_LINEA = 8

# ── Giro brusco (90°) ──────────────────────────────────────────
# Si el error supera ERR_90 durante N frames seguidos → modo GIRO_BRUSCO
# En este modo: velocidad mínima + sin fusión ROI lejano + recovery lateral
FRAMES_CONFIRMA_90   = 2    # frames consecutivos con error > ERR_90 para activar
FRAMES_SALIDA_90     = 6    # frames con error < ERR_CURVA para desactivar

# ══════════════════════════════════════════════════════════════
#  CÁMARA
# ══════════════════════════════════════════════════════════════
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cam.isOpened():
    print("Error: cámara no disponible.")
    sys.exit()

Movimiento.setVelocidad(VEL_CURVA)

# ══════════════════════════════════════════════════════════════
#  ESTADO GLOBAL
# ══════════════════════════════════════════════════════════════
cont_perdido      = 0
ultimo_error      = 0
ultimo_giro       = 0
en_interseccion   = False
modo_giro_brusco  = False   # ← NUEVO
frames_error_alto = 0       # ← NUEVO: contador para confirmar 90°
frames_error_bajo = 0       # ← NUEVO: contador para salir del modo 90°

# ══════════════════════════════════════════════════════════════
#  PREPROCESADO
# ══════════════════════════════════════════════════════════════
def preprocesar_roi(frame, y_ini, y_fin):
    crop  = frame[y_ini:y_fin, 0:640]
    gray  = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (7, 7), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    k     = np.ones((5, 5), np.uint8)
    th    = cv2.morphologyEx(th, cv2.MORPH_CLOSE, k)
    th    = cv2.morphologyEx(th, cv2.MORPH_OPEN,  k)
    return crop, th

# ══════════════════════════════════════════════════════════════
#  ANÁLISIS DE CONTORNOS
# ══════════════════════════════════════════════════════════════
def analizar_contornos(thresh):
    h = thresh.shape[0]
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidatos = []
    for c in contornos:
        area = cv2.contourArea(c)
        if area < AREA_MIN or area > AREA_MAX:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        if cx < 20 or cx > 620:
            continue

        p_area  = min(area / 20000.0, 1.5)
        p_y     = cy / h
        rect    = cv2.minAreaRect(c)
        w, h_r  = rect[1]
        asp     = (max(w, h_r) / min(w, h_r)) if min(w, h_r) > 0 else 1.0
        p_elong = min(asp / 8.0, 1.0)
        punt    = p_area + p_y + p_elong

        angulo = rect[2]
        if angulo < -45:
            angulo += 90

        candidatos.append((punt, cx, cy, area, angulo, c))

    candidatos.sort(key=lambda x: x[0], reverse=True)
    return candidatos

# ══════════════════════════════════════════════════════════════
#  LÍNEAS PARALELAS
# ══════════════════════════════════════════════════════════════
def obtener_grosor(contorno):
    rect = cv2.minAreaRect(contorno)
    w, h = rect[1]
    return min(w, h)

def son_paralelas(ang1, ang2, tolerancia=ANGULO_PARALELO):
    diff = abs(ang1 - ang2)
    diff = min(diff, abs(diff - 90))
    return diff <= tolerancia

def filtrar_paralelas_y_elegir_mas_gorda(candidatos):
    if len(candidatos) < 2:
        return None
    n = len(candidatos)
    pertenece = list(range(n))

    def find(x):
        while pertenece[x] != x:
            pertenece[x] = pertenece[pertenece[x]]
            x = pertenece[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            pertenece[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if son_paralelas(candidatos[i][4], candidatos[j][4]):
                union(i, j)

    grupos = {}
    for i in range(n):
        grupos.setdefault(find(i), []).append(i)

    grupo_paralelo = max(
        (g for g in grupos.values() if len(g) >= 2),
        key=len, default=None
    )
    if grupo_paralelo is None:
        return None

    mejor = max(grupo_paralelo, key=lambda i: obtener_grosor(candidatos[i][5]))
    grosor_elegido = obtener_grosor(candidatos[mejor][5])

    if grosor_elegido < GROSOR_MIN_LINEA:
        return None

    return candidatos[mejor], grosor_elegido, len(grupo_paralelo)

# ══════════════════════════════════════════════════════════════
#  INTERSECCIÓN
# ══════════════════════════════════════════════════════════════
def detectar_interseccion(candidatos):
    grandes = [x for x in candidatos if x[3] > AREA_INTERSECCION]
    return len(grandes) >= N_INTERSECCION

# ══════════════════════════════════════════════════════════════
#  SELECTOR DE CONTORNO
# ══════════════════════════════════════════════════════════════
def elegir_contorno(candidatos, error_previo):
    if not candidatos:
        return None

    # Prioridad 1: paralelas → más gorda
    res_par = filtrar_paralelas_y_elegir_mas_gorda(candidatos)
    if res_par is not None:
        datos, grosor, n_par = res_par
        if DEBUG:
            print(f"\n[PARALELAS] {n_par} líneas | grosor:{grosor:.1f}px", end='')
        return datos, False

    # Prioridad 2: intersección → más cercana a trayectoria
    if detectar_interseccion(candidatos):
        grandes  = [x for x in candidatos if x[3] > AREA_INTERSECCION]
        objetivo = CENTRO_X + error_previo
        mejor    = min(grandes, key=lambda x: abs(x[1] - objetivo))
        return mejor, True

    # Prioridad 3: normal → mayor puntuación
    return candidatos[0], False

# ══════════════════════════════════════════════════════════════
#  DETECCIÓN Y GESTIÓN DE GIRO DE 90°  ← NUEVO BLOQUE
# ══════════════════════════════════════════════════════════════
def actualizar_modo_giro_brusco(error_abs):
    """
    Máquina de estados de 2 estados: NORMAL ↔ GIRO_BRUSCO.

    Entrada:  error_abs (valor absoluto del error X actual)
    Modifica: modo_giro_brusco, frames_error_alto, frames_error_bajo
    """
    global modo_giro_brusco, frames_error_alto, frames_error_bajo

    if not modo_giro_brusco:
        # ── Condición de ACTIVACIÓN ────────────────────────────
        if error_abs > ERR_90:
            frames_error_alto += 1
            frames_error_bajo  = 0
            if frames_error_alto >= FRAMES_CONFIRMA_90:
                modo_giro_brusco = True
                if DEBUG:
                    print("\n[90°] ACTIVADO", end='')
        else:
            frames_error_alto = 0
    else:
        # ── Condición de DESACTIVACIÓN ─────────────────────────
        if error_abs < ERR_CURVA:
            frames_error_bajo += 1
            if frames_error_bajo >= FRAMES_SALIDA_90:
                modo_giro_brusco = False
                frames_error_alto = 0
                frames_error_bajo = 0
                if DEBUG:
                    print("\n[90°] DESACTIVADO", end='')
        else:
            frames_error_bajo = 0

# ══════════════════════════════════════════════════════════════
#  VELOCIDAD Y MOVIMIENTO
# ══════════════════════════════════════════════════════════════
def calcular_velocidad(error, interseccion):
    if modo_giro_brusco:
        return VEL_90           # ← siempre mínimo en 90°
    if interseccion:
        return VEL_GIRO
    if abs(error) < ERR_RECTA:
        return VEL_RECTA
    elif abs(error) < ERR_CURVA:
        return VEL_CURVA
    return VEL_GIRO

def aplicar_movimiento(error_final, vel):
    global ultimo_giro
    Movimiento.setVelocidad(vel)

    if abs(error_final) <= ZONA_MUERTA:
        Movimiento.Avanza()
        ultimo_giro = 0
        return "AVANZA"
    elif error_final > 0:
        Movimiento.Derecha()
        ultimo_giro = 1
        return f"DERECHA  (P={int(KP * error_final):+d})"
    else:
        Movimiento.Izquierda()
        ultimo_giro = -1
        return f"IZQUIERDA(P={int(KP * error_final):+d})"

# ══════════════════════════════════════════════════════════════
#  RECUPERACIÓN
# ══════════════════════════════════════════════════════════════
def recuperar(n_perdido):
    """
    En modo GIRO_BRUSCO: gira hacia el último lado (la línea está ahí).
    En modo normal:      ídem pero a velocidad más baja.
    Nunca retrocede.
    """
    if n_perdido >= MAX_PERDIDO:
        Movimiento.Stop()
        return "STOP"

    vel = VEL_90 if modo_giro_brusco else VEL_RECOVERY
    Movimiento.setVelocidad(vel)

    if ultimo_giro > 0:
        Movimiento.Derecha()
        return f"RECOVERY → DERECHA ({'90°' if modo_giro_brusco else 'normal'})"
    elif ultimo_giro < 0:
        Movimiento.Izquierda()
        return f"RECOVERY → IZQUIERDA ({'90°' if modo_giro_brusco else 'normal'})"
    else:
        Movimiento.Avanza()
        return "RECOVERY → AVANZA"

# ══════════════════════════════════════════════════════════════
#  BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════
print("Siguelíneas v4 — 90° fix. 'q' para salir.")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error de captura.")
        break

    # ── 1. Procesar ROI ────────────────────────────────────────
    crop_c, th_c = preprocesar_roi(frame, *ROI_CERCA)
    crop_l, th_l = preprocesar_roi(frame, *ROI_LEJOS)

    cands_cerca = analizar_contornos(th_c)
    cands_lejos = analizar_contornos(th_l)

    # ── 2. Contorno principal ──────────────────────────────────
    resultado_cerca = elegir_contorno(cands_cerca, ultimo_error)

    if resultado_cerca is not None:
        datos_c, es_interseccion = resultado_cerca
        _, cx_c, cy_c, area_c, ang_c, cont_c = datos_c

        error_cerca = cx_c - CENTRO_X
        error_final = error_cerca

        # ── 3. Actualizar modo 90° ANTES de fusionar ──────────
        actualizar_modo_giro_brusco(abs(error_cerca))

        # ── 4. Fusión con ROI lejano ───────────────────────────
        #   Desactivada en modo 90° y en intersecciones:
        #   en un giro brusco la zona lejana muestra la línea
        #   perpendicular y confunde el error
        if not es_interseccion and not modo_giro_brusco and cands_lejos:
            cx_l        = cands_lejos[0][1]
            error_lejos = cx_l - CENTRO_X
            error_final = int(error_cerca * (1 - PESO_LEJOS) + error_lejos * PESO_LEJOS)

        # ── 5. Control proporcional ────────────────────────────
        error_p = int(KP * error_final)
        vel     = calcular_velocidad(error_final, es_interseccion)
        accion  = aplicar_movimiento(error_final, vel)

        ultimo_error    = error_final
        cont_perdido    = 0
        en_interseccion = es_interseccion

        # ── 6. Debug ───────────────────────────────────────────
        if DEBUG:
            display    = frame.copy()
            grosor_vis = obtener_grosor(cont_c)

            cv2.rectangle(display, (0, ROI_CERCA[0]), (639, ROI_CERCA[1]), (0, 255, 100), 1)
            cv2.rectangle(display, (0, ROI_LEJOS[0]), (639, ROI_LEJOS[1]), (255, 200, 0) if not modo_giro_brusco else (80, 80, 80), 1)

            cont_full = cont_c.copy()
            cont_full[:, :, 1] += ROI_CERCA[0]
            cv2.drawContours(display, [cont_full], -1, (0, 165, 255), 2)

            box = cv2.boxPoints(cv2.minAreaRect(cont_c)).astype(int)
            box[:, 1] += ROI_CERCA[0]
            cv2.polylines(display, [box], True, (255, 100, 0), 1)

            cv2.circle(display, (cx_c, cy_c + ROI_CERCA[0]), 8, (0, 255, 0), -1)
            cv2.line(display, (CENTRO_X, 0), (CENTRO_X, 480), (200, 80, 0), 1)

            if not es_interseccion and not modo_giro_brusco and cands_lejos:
                cx_l_abs = cands_lejos[0][1]
                cy_l_abs = cands_lejos[0][2] + ROI_LEJOS[0]
                cv2.circle(display, (cx_l_abs, cy_l_abs), 6, (255, 200, 0), -1)

            # Etiqueta de modo
            if modo_giro_brusco:
                modo_label = "[GIRO 90°]"
                modo_color = (0, 0, 255)
            elif es_interseccion:
                modo_label = "[INTERSECCION]"
                modo_color = (0, 50, 255)
            elif grosor_vis > GROSOR_MIN_LINEA and len(cands_cerca) > 1:
                modo_label = f"[PARALELAS] grosor:{grosor_vis:.0f}px"
                modo_color = (255, 80, 200)
            else:
                modo_label = ""
                modo_color = (180, 180, 0)

            cv2.putText(display, f"ErrX:{error_final:+d} P:{error_p:+d} Vel:{vel}  {accion}", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 0) if "AVANZA" in accion else (0, 140, 255), 2)
            cv2.putText(display, f"Area:{int(area_c)}  Ang:{ang_c:.1f}  {modo_label}", (8, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.48, modo_color, 1)
            cv2.putText(display, f"Grosor:{grosor_vis:.0f}px  Cands:{len(cands_cerca)}" f"  90°frames:{frames_error_alto}", (8, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (180, 180, 0), 1)

            th_c_bgr   = cv2.cvtColor(cv2.resize(th_c, (320, 80)), cv2.COLOR_GRAY2BGR)
            th_l_bgr   = cv2.cvtColor(cv2.resize(th_l, (320, 80)), cv2.COLOR_GRAY2BGR)
            disp_small = cv2.resize(display, (320, 240))
            panel      = np.vstack([th_c_bgr, th_l_bgr, np.zeros((80, 320, 3), np.uint8)])
            cv2.imshow("v4 | Frame | ROI_C | ROI_L", np.hstack([disp_small, panel]))

    else:
        cont_perdido += 1
        accion = recuperar(cont_perdido)

        if DEBUG:
            display = frame.copy()
            cv2.putText(display, f"PERDIDO ({cont_perdido}/{MAX_PERDIDO})  {accion}", (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            th_c_bgr   = cv2.cvtColor(cv2.resize(th_c, (320, 80)), cv2.COLOR_GRAY2BGR)
            disp_small = cv2.resize(display, (320, 240))
            panel      = np.vstack([th_c_bgr, np.zeros((160, 320, 3), np.uint8)])
            cv2.imshow("v4 | Frame | ROI_C | ROI_L", np.hstack([disp_small, panel]))

    if DEBUG:
        print(f"[{'OK' if resultado_cerca else '!!':2}] "
            f"Err:{ultimo_error:+4d}  "
            f"Perdido:{cont_perdido:2d}  "
            f"{'[90°]  ' if modo_giro_brusco else '       '}"
            f"{'[CRUCE]' if en_interseccion else '       '}",
            end='\r')

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ══════════════════════════════════════════════════════════════
#  LIMPIEZA
# ══════════════════════════════════════════════════════════════
print("\nCerrando...")
cam.release()
cv2.destroyAllWindows()
Movimiento.Stop()
Movimiento.setVelocidad(0)