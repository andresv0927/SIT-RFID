"""
main.py
Punto de entrada del módulo de reconocimiento de placas SIT-RFID.
"""
import numpy as np
import cv2
import sys
import os
import argparse
import time
from collections import deque, Counter

sys.path.insert(0, os.path.dirname(__file__))

from camera_capture import CameraCapture
from plate_detector import PlateDetector
from ocr_reader import OCRReader
from plate_validator import PlateValidator
from api_client import send_detection          # ← integración con el backend
from utils.logger import get_logger

logger = get_logger("main")

# ──────────────────────────────────────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────────────────────────────────────
FRAME_SKIP        = 15    # procesar 1 de cada N frames
CONFIDENCE_MIN    = 0.0   # sin filtro de confianza
COOLDOWN_SECONDS  = 4.0   # segundos entre lecturas de la misma placa
SMOOTHING_FRAMES  = 8     # frames para suavizar el bounding box
CONFIRM_THRESHOLD = 3     # veces que debe aparecer la misma placa para confirmarla
HISTORY_SIZE      = 10    # tamaño del historial de lecturas OCR


# ──────────────────────────────────────────────────────────────────────────────
class BoxStabilizer:
    """Suaviza la posición del recuadro usando promedio móvil."""

    def __init__(self, history=SMOOTHING_FRAMES):
        self.boxes = deque(maxlen=history)

    def update(self, box):
        if box is not None:
            self.boxes.append(box)

    def get_stable_box(self):
        if not self.boxes:
            return None
        x = int(sum(b[0] for b in self.boxes) / len(self.boxes))
        y = int(sum(b[1] for b in self.boxes) / len(self.boxes))
        w = int(sum(b[2] for b in self.boxes) / len(self.boxes))
        h = int(sum(b[3] for b in self.boxes) / len(self.boxes))
        return (x, y, w, h)

    def clear(self):
        self.boxes.clear()


# ──────────────────────────────────────────────────────────────────────────────
class PlateConfirmer:
    """Confirma una placa cuando aparece CONFIRM_THRESHOLD veces en el historial."""

    def __init__(self):
        self.history = deque(maxlen=HISTORY_SIZE)

    def add(self, text):
        if text and len(text) >= 3:
            self.history.append(text)

    def get_confirmed(self):
        if len(self.history) < CONFIRM_THRESHOLD:
            return None, 0
        counter = Counter(self.history)
        most_common, count = counter.most_common(1)[0]
        score = (count / len(self.history)) * 100
        if count >= CONFIRM_THRESHOLD:
            return most_common, round(score, 1)
        return None, 0

    def reset(self):
        self.history.clear()


# ──────────────────────────────────────────────────────────────────────────────
def draw_overlay(frame, stable_box, confirmed_plate, validator, backend_status=None):
    h_frame, w_frame = frame.shape[:2]

    if stable_box:
        x, y, w, h = stable_box
        color = (0, 255, 0) if confirmed_plate else (0, 200, 255)
        thickness = 3
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        corner_len = 15
        for cx, cy in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
            dx = corner_len if cx == x else -corner_len
            dy = corner_len if cy == y else -corner_len
            cv2.line(frame, (cx, cy), (cx + dx, cy), color, thickness + 1)
            cv2.line(frame, (cx, cy), (cx, cy + dy), color, thickness + 1)

    if confirmed_plate:
        result = validator.validate(confirmed_plate)
        panel_y = h_frame - 110
        cv2.rectangle(frame, (0, panel_y), (w_frame, h_frame), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, panel_y), (w_frame, h_frame), (0, 255, 0), 2)

        placa_str  = f"PLACA: {result['plate']}"
        tipo_str   = f"TIPO:  {result['type'].upper()}"
        valida_str = "VALIDA" if result["valid"] else "NO VALIDA"
        val_color  = (0, 255, 0) if result["valid"] else (0, 0, 255)

        cv2.putText(frame, placa_str,  (15, panel_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, tipo_str,   (15, panel_y + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        cv2.putText(frame, valida_str, (w_frame - 180, panel_y + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, val_color, 2)

        # ── Mensaje del backend en el overlay ────────────────────────────────
        if backend_status:
            b_color = (0, 200, 100) if "Turno" in backend_status else (0, 140, 255)
            cv2.putText(frame, backend_status, (15, panel_y + 82),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, b_color, 1)
    else:
        cv2.putText(frame, "Apunta la camara a la placa",
                    (10, h_frame - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

    return frame


# ──────────────────────────────────────────────────────────────────────────────
def run_realtime(camera_index=0):
    print("=== SIT-RFID | Reconocimiento de Placas ===")
    print("Presiona Q para salir | R para resetear\n")

    detector   = PlateDetector()
    reader     = OCRReader()
    validator  = PlateValidator()
    stabilizer = BoxStabilizer()
    confirmer  = PlateConfirmer()

    last_confirmed  = ""
    last_time       = 0
    frame_count     = 0
    stable_box      = None
    confirmed_plate = None
    backend_status  = None

    with CameraCapture(source=camera_index) as cam:
        while True:
            frame = cam.read_frame()
            if frame is None:
                break

            frame_count += 1
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):
                confirmer.reset()
                stabilizer.clear()
                confirmed_plate = None
                last_confirmed  = ""
                backend_status  = None
                print("\n[RESET] Lectura reiniciada.\n")

            if frame_count % FRAME_SKIP == 0:
                plate_crop, annotated_frame = detector.detect(frame)

                if plate_crop is not None:
                    stabilizer.update(_infer_box(frame, annotated_frame))

                    text, confidence = reader.read_with_confidence(plate_crop)

                    if len(text) >= 3:
                        confirmer.add(text)

                    candidate, score = confirmer.get_confirmed()
                    if candidate:
                        res = validator.validate(candidate)
                        if res["valid"]:
                            confirmed_plate = candidate
                            now = time.time()
                            if (candidate != last_confirmed or
                                    now - last_time > COOLDOWN_SECONDS):
                                last_confirmed = candidate
                                last_time      = now
                                backend_status = _print_result(res, score)
                        else:
                            print(f"[INFO] Texto no válido como placa: {candidate}")
                else:
                    stabilizer.update(None)

                stable_box = stabilizer.get_stable_box()

            display = frame.copy()
            display = draw_overlay(display, stable_box, confirmed_plate,
                                   validator, backend_status)
            cv2.imshow("SIT-RFID | Reconocimiento de Placas", display)

    print("\nSesión finalizada.")


# ──────────────────────────────────────────────────────────────────────────────
def _infer_box(frame, annotated_frame):
    lower_green = np.array([0, 200, 0])
    upper_green = np.array([80, 255, 80])
    mask = cv2.inRange(annotated_frame, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    return (x, y, w, h)


# ──────────────────────────────────────────────────────────────────────────────
def _print_result(result, score) -> str:
    """
    Imprime resultado en consola, envía al backend y retorna
    un string corto para mostrar en el overlay de la cámara.
    """
    print(f"\n{'='*45}")
    print(f"  ✅ PLACA CONFIRMADA  : {result['plate']}")
    print(f"     TIPO              : {result['type'].upper()}")
    print(f"     SCORE CONFIANZA   : {score:.0f}%")

    # ── Enviar al backend ─────────────────────────────────────────────────────
    resp = send_detection(
        plate=result["plate"],
        plate_type=result["type"],
        confidence=score
    )

    if resp.get("error") == "Backend offline":
        msg = "Backend offline - sin registro"
        print(f"  ⚠️  {msg}")

    elif resp.get("already_registered"):
        msg = "YA REGISTRADA - no se duplico en BD"
        print(f"  ⚠️  {msg}")

    elif resp.get("turn_number"):
        msg = f"Turno #{resp['turn_number']} asignado"
        print(f"  🎫 {msg}")

    else:
        msg = resp.get("message", "Registrado")
        print(f"  ℹ️  {msg}")

    print(f"{'='*45}\n")
    return msg


# ──────────────────────────────────────────────────────────────────────────────
def run_from_image(image_path):
    if not os.path.exists(image_path):
        print(f"[ERROR] Imagen no encontrada: {image_path}")
        return
    frame     = cv2.imread(image_path)
    detector  = PlateDetector()
    reader    = OCRReader()
    validator = PlateValidator()
    plate_crop, annotated = detector.detect(frame)
    if plate_crop is not None:
        text, conf = reader.read_with_confidence(plate_crop)
        result = validator.validate(text)
        _print_result(result, conf)
        cv2.imshow("Resultado", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("\n[!] No se detectó placa en la imagen.\n")


# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SIT-RFID — Reconocimiento de placas")
    parser.add_argument("--image",  type=str, default=None)
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    if args.image:
        run_from_image(args.image)
    else:
        run_realtime(camera_index=args.camera)


if __name__ == "__main__":
    main()