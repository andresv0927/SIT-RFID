"""
ocr_reader.py
"""
import re
import pytesseract
import cv2
import numpy as np
from utils.image_utils import preprocess_for_ocr
from utils.logger import get_logger

logger = get_logger("ocr_reader")

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class OCRReader:

    def read_with_confidence(self, plate_image):
        if plate_image is None or plate_image.size == 0:
            return "", 0

        processed = preprocess_for_ocr(plate_image)
        cv2.imwrite("debug_plate.png", processed)

        best_text = ""
        best_conf = 0

        # ← QUITAMOS lang="spa" para evitar errores
        for psm in [11, 8, 13, 7, 6]:
            config = (
                f"--psm {psm} --oem 3 "
                f"-c tessedit_char_whitelist={WHITELIST}"
            )
            try:
                raw = pytesseract.image_to_string(
                    processed, config=config
                )
                clean = self._clean(raw)

                if len(clean) >= 3:
                    # Calcular confianza con image_to_data
                    data = pytesseract.image_to_data(
                        processed,
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    confs = [int(c) for c in data["conf"]
                             if str(c).isdigit() and int(c) > 0]
                    avg_conf = sum(confs) / len(confs) if confs else 50

                    if len(clean) > len(best_text):
                        best_text = clean
                        best_conf = avg_conf

            except Exception as e:
                print(f"[ERROR] PSM {psm}: {e}")
                continue

        return best_text, round(best_conf, 1)

    def read(self, plate_image):
        text, _ = self.read_with_confidence(plate_image)
        return text

    @staticmethod
    def _clean(text):
        return re.sub(r"[^A-Z0-9]", "", text.upper())