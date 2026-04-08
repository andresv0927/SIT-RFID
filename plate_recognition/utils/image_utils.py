"""
utils/image_utils.py
Preprocesamiento optimizado para placas colombianas.
"""

import cv2
import numpy as np


def resize_image(image, width=640):
    h, w = image.shape[:2]
    ratio = width / w
    return cv2.resize(image, (width, int(h * ratio)), interpolation=cv2.INTER_AREA)


def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def apply_blur(image, kernel_size=(5, 5)):
    return cv2.GaussianBlur(image, kernel_size, 0)


def apply_threshold(image):
    return cv2.adaptiveThreshold(
        image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )


def apply_morphology(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)


def preprocess_for_ocr(image):
    """
    Pipeline limpio y simple.
    Menos pasos = menos daño a la imagen.
    """
    # 1. Escalar x2 solamente (x3 o x4 distorsiona con cámaras malas)
    img = cv2.resize(image, None, fx=2, fy=2,
                     interpolation=cv2.INTER_LINEAR)

    # 2. Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Enfocar con kernel sharpening
    kernel_sharp = np.array([
        [ 0, -1,  0],
        [-1,  5, -1],
        [ 0, -1,  0]
    ])
    gray = cv2.filter2D(gray, -1, kernel_sharp)

    # 4. Threshold simple de Otsu (NO adaptativo, menos agresivo)
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # 5. Verificar que el fondo sea blanco (texto oscuro)
    # Si hay más negro que blanco, invertir
    white = cv2.countNonZero(thresh)
    black = thresh.size - white
    if black > white:
        thresh = cv2.bitwise_not(thresh)

    # 6. Padding mínimo
    thresh = cv2.copyMakeBorder(
        thresh, 10, 10, 10, 10,
        cv2.BORDER_CONSTANT, value=255
    )

    return thresh


def draw_plate_box(image, contour, label=""):
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    if label:
        cv2.putText(image, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    return image


def save_image(image, path):
    cv2.imwrite(path, image)