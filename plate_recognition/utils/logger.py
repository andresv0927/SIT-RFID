"""
utils/logger.py
Sistema de logging centralizado para SIT-RFID.
"""

import logging
import os
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger configurado con salida a consola y archivo.
    
    Args:
        name: nombre del módulo (ej: 'plate_detector', 'ocr_reader')
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # ya fue configurado antes

    logger.setLevel(logging.DEBUG)

    # --- Formato ---
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # --- Handler: consola ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # --- Handler: archivo ---
    log_dir = os.path.join(os.path.dirname(__file__), "..", "data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"sit_rfid_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger