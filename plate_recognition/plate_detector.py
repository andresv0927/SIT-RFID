"""
plate_detector.py
Detecta placas colombianas usando su color amarillo/naranja característico.
"""

import cv2
import numpy as np
from utils.image_utils import resize_image
from utils.logger import get_logger

logger = get_logger("plate_detector")


class PlateDetector:

    def detect(self, frame):
        annotated = frame.copy()
        img = resize_image(frame, width=640)
        h_scale = frame.shape[0] / img.shape[0]
        w_scale = frame.shape[1] / img.shape[1]

        # Convertir a HSV para detectar color amarillo/naranja de placas colombianas
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Rango de amarillo/naranja en HSV
        lower_yellow = np.array([15, 80, 80])
        upper_yellow = np.array([35, 255, 255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # También detectar blanco (placas blancas)
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 40, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)

        # Combinar ambas máscaras
        mask = cv2.bitwise_or(mask_yellow, mask_white)

        # Limpiar máscara
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return None, annotated

        plate_candidates = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h

            if area < 2000 or area > 80000:
                continue
            if w < 60 or h < 15:
                continue

            aspect_ratio = w / h
            if not (1.5 <= aspect_ratio <= 6.5):
                continue

            plate_candidates.append((area, x, y, w, h))

        if not plate_candidates:
            # Fallback: usar detección por contornos clásica
            return self._detect_by_contours(frame)

        plate_candidates.sort(reverse=True)
        _, x, y, w, h = plate_candidates[0]

        # Escalar al frame original
        x = int(x * w_scale)
        y = int(y * h_scale)
        w = int(w * w_scale)
        h = int(h * h_scale)

        # Padding
        pad_x, pad_y = 5, 5
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(frame.shape[1], x + w + pad_x)
        y2 = min(frame.shape[0], y + h + pad_y)

        plate_crop = frame[y1:y2, x1:x2]

        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(annotated, "PLACA", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        logger.info(f"Placa detectada en: x={x}, y={y}, w={w}, h={h}")
        return plate_crop, annotated

    def _detect_by_contours(self, frame):
        """Fallback: detección clásica por bordes."""
        annotated = frame.copy()
        img = resize_image(frame, width=640)
        h_scale = frame.shape[0] / img.shape[0]
        w_scale = frame.shape[1] / img.shape[1]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
        edges = cv2.Canny(bilateral, 30, 200)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            if area < 2000 or area > 50000:
                continue
            ar = w / h
            if not (2.0 <= ar <= 6.0):
                continue

            x = int(x * w_scale)
            y = int(y * h_scale)
            w = int(w * w_scale)
            h = int(h * h_scale)

            plate_crop = frame[y:y+h, x:x+w]
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(annotated, "PLACA", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            logger.info(f"Placa detectada (fallback): x={x}, y={y}, w={w}, h={h}")
            return plate_crop, annotated

        return None, annotated

    def detect_from_file(self, image_path):
        import os
        if not os.path.exists(image_path):
            logger.error(f"Imagen no encontrada: {image_path}")
            return None, None
        frame = cv2.imread(image_path)
        return self.detect(frame)