"""
camera_capture.py
Maneja la captura de frames desde la webcam o desde una imagen/video.
"""

import cv2
from utils.logger import get_logger

logger = get_logger("camera_capture")


class CameraCapture:
    """
    Wrapper sobre cv2.VideoCapture para simplificar la captura.

    Args:
        source: índice de cámara (0 = webcam por defecto) o ruta a video/imagen.
    """

    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def open(self):
        """Abre la cámara o el archivo de video."""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            logger.error(f"No se pudo abrir la fuente: {self.source}")
            raise RuntimeError(f"No se puede abrir la cámara/video: {self.source}")
        logger.info(f"Cámara abierta correctamente (fuente: {self.source})")

    def read_frame(self):
        """
        Lee un frame.

        Returns:
            frame (np.ndarray) o None si falla.
        """
        if self.cap is None:
            logger.warning("Cámara no inicializada. Llama a open() primero.")
            return None

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("No se pudo leer el frame.")
            return None
        return frame

    def release(self):
        """Libera los recursos de la cámara."""
        if self.cap:
            self.cap.release()
            logger.info("Cámara liberada.")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.release()
        cv2.destroyAllWindows()


def capture_single_frame(source=0):
    """
    Captura un único frame y cierra la cámara.
    Útil para pruebas rápidas.
    """
    with CameraCapture(source) as cam:
        frame = cam.read_frame()
    return frame