# =============================================================================
#  vision_module.py  –  Visión por computador con webcam
#
#  Dos tareas en el mismo módulo (mismo frame):
#   1. Detección de línea/borde de la lona → evitar salirse del ring
#   2. Detección del robot rival (blanco sobre lona blanca → bordes/contornos)
#
#  NOTA sobre robots blancos en lona blanca:
#   Dado que rival y lona son del mismo color, la cámara se usa como apoyo
#   secundario al LiDAR. La detección visual se basa en:
#     · Diferencias de textura y sombra (bordes del rival proyectan sombra)
#     · Detección de contornos por gradiente (Canny)
#     · Opcionalmente: fondo de referencia para detección por diferencia
# =============================================================================

import cv2
import numpy as np
import threading
import time
from config import (
    CAMERA_INDEX,
    LINE_DETECTION_METHOD,
    LINE_DARK_THRESHOLD,
    LINE_LIGHT_THRESHOLD,
    LINE_PIXEL_RATIO,
    LINE_ROI_HEIGHT,
    RIVAL_MIN_AREA,
    RIVAL_MAX_AREA,
    RIVAL_CENTER_MARGIN,
)


class VisionSystem:
    """
    Captura frames de la webcam en un hilo y expone:
      · line_detected      – bool: hay borde de lona cerca
      · line_side          – 'izquierda' | 'derecha' | 'centro' | None
      · rival_visible      – bool: rival visto por cámara
      · rival_offset_px    – píxeles de desplazamiento del rival respecto al centro
      · debug_frame        – frame anotado para depuración (opcional)
    """

    def __init__(self, show_debug: bool = False):
        self._lock           = threading.Lock()
        self._line_detected  = False
        self._line_side      = None
        self._rival_visible  = False
        self._rival_offset   = 0       # px, positivo = rival a la derecha
        self._debug_frame    = None
        self._show_debug     = show_debug
        self._running        = False
        self._thread         = None
        self._background     = None    # Frame de referencia para substracción

        self._cap = cv2.VideoCapture(CAMERA_INDEX)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._cap.set(cv2.CAP_PROP_FPS,          30)

        if not self._cap.isOpened():
            raise RuntimeError(f"[Visión] No se pudo abrir la cámara (índice {CAMERA_INDEX}).")

    # ── API pública ──────────────────────────────────────────────────────────

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        print("[Visión] Sistema de visión iniciado.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self._cap.release()
        cv2.destroyAllWindows()
        print("[Visión] Sistema de visión detenido.")

    def calibrate_background(self):
        """
        Captura varios frames del ring vacío para usarlos como referencia.
        Llamar al inicio, antes de que los robots entren al ring.
        """
        frames = []
        for _ in range(15):
            ret, frame = self._cap.read()
            if ret:
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32))
            time.sleep(0.05)
        if frames:
            self._background = np.mean(frames, axis=0).astype(np.uint8)
            print("[Visión] Fondo de referencia calibrado.")

    @property
    def line_detected(self) -> bool:
        with self._lock:
            return self._line_detected

    @property
    def line_side(self):
        with self._lock:
            return self._line_side

    @property
    def rival_visible(self) -> bool:
        with self._lock:
            return self._rival_visible

    @property
    def rival_offset_px(self) -> int:
        """Offset del rival en píxeles respecto al centro (+ = derecha)."""
        with self._lock:
            return self._rival_offset

    @property
    def debug_frame(self):
        with self._lock:
            return self._debug_frame.copy() if self._debug_frame is not None else None

    # ── Captura y procesamiento ──────────────────────────────────────────────

    def _capture_loop(self):
        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            h, w = frame.shape[:2]
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            debug = frame.copy() if self._show_debug else None

            # ── 1. Detección de línea (borde de la lona) ──────────────────
            line_det, line_side = self._detect_line(gray, w, h, debug)

            # ── 2. Detección del rival ─────────────────────────────────────
            rival_vis, rival_off = self._detect_rival(gray, w, h, debug)

            with self._lock:
                self._line_detected = line_det
                self._line_side     = line_side
                self._rival_visible = rival_vis
                self._rival_offset  = rival_off
                if debug is not None:
                    self._debug_frame = debug

            if self._show_debug and debug is not None:
                cv2.imshow("Sumo Debug", debug)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self._running = False

    # ── Detección de línea ───────────────────────────────────────────────────

    def _detect_line(self, gray, w, h, debug):
        """
        Analiza la franja inferior de la imagen buscando el borde de la lona.
        La lona sumo estándar es NEGRA con borde BLANCO en el ring clásico,
        pero aquí la lona es BLANCA → detectamos la banda OSCURA exterior.
        """
        roi = gray[h - LINE_ROI_HEIGHT:h, :]

        if LINE_DETECTION_METHOD == "dark":
            mask = (roi < LINE_DARK_THRESHOLD).astype(np.uint8) * 255
        else:
            mask = (roi > LINE_LIGHT_THRESHOLD).astype(np.uint8) * 255

        # Morfología para limpiar ruido
        kernel = np.ones((3, 3), np.uint8)
        mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # ¿Hay suficientes píxeles de línea?
        ratio = np.sum(mask > 0) / (w * LINE_ROI_HEIGHT)
        detected = ratio > LINE_PIXEL_RATIO

        # ¿En qué lado está la línea?
        side = None
        if detected:
            left_sum  = np.sum(mask[:, :w // 2] > 0)
            right_sum = np.sum(mask[:, w // 2:] > 0)
            if left_sum > right_sum * 1.5:
                side = "izquierda"
            elif right_sum > left_sum * 1.5:
                side = "derecha"
            else:
                side = "centro"

        if debug is not None and detected:
            cv2.rectangle(debug,
                          (0, h - LINE_ROI_HEIGHT), (w, h),
                          (0, 0, 255), 2)
            cv2.putText(debug, f"LINEA: {side}", (10, h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return detected, side

    # ── Detección de rival ───────────────────────────────────────────────────

    def _detect_rival(self, gray, w, h, debug):
        """
        El rival es blanco como la lona → detección por gradiente (Canny) y
        opcionalmente por diferencia con el fondo de referencia.
        Se busca un contorno pequeño con las dimensiones de un mini-sumo.
        """
        # Zona de análisis: descartamos la franja inferior (zona de línea)
        analysis_h = h - LINE_ROI_HEIGHT
        roi_gray   = gray[:analysis_h, :]

        # ── Método A: Diferencia con fondo calibrado (si está disponible) ──
        if self._background is not None:
            bg_roi = self._background[:analysis_h, :]
            diff   = cv2.absdiff(roi_gray, bg_roi)
            _, diff_mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            kernel = np.ones((5, 5), np.uint8)
            diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_CLOSE, kernel)
            work_mask = diff_mask
        else:
            # ── Método B: Detección por bordes (Canny) ─────────────────────
            blurred   = cv2.GaussianBlur(roi_gray, (5, 5), 0)
            edges     = cv2.Canny(blurred, 30, 90)
            kernel    = np.ones((3, 3), np.uint8)
            work_mask = cv2.dilate(edges, kernel, iterations=2)

        contours, _ = cv2.findContours(work_mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        best_contour = None
        best_area    = 0
        cx_frame     = w // 2

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if RIVAL_MIN_AREA < area < RIVAL_MAX_AREA:
                x, y, cw, ch = cv2.boundingRect(cnt)
                aspect = cw / ch if ch > 0 else 0
                # Los mini-sumo suelen ser más o menos cuadrados (0.5 – 2.5)
                if 0.4 < aspect < 3.0:
                    if area > best_area:
                        best_area    = area
                        best_contour = cnt

        if best_contour is not None:
            M  = cv2.moments(best_contour)
            if M["m00"] > 0:
                cx  = int(M["m10"] / M["m00"])
                cy  = int(M["m01"] / M["m00"])
                off = cx - cx_frame

                if debug is not None:
                    cv2.drawContours(debug, [best_contour], -1, (0, 255, 0), 2)
                    cv2.circle(debug, (cx, cy), 5, (0, 255, 0), -1)
                    cv2.putText(debug, f"RIVAL off={off:+d}px",
                                (cx + 8, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                return True, off

        return False, 0
