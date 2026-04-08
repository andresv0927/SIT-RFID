"""
plate_validator.py
Valida que el texto OCR corresponda al formato oficial de placas colombianas.

Formatos:
  - Vehículo particular / público: ABC123  (3 letras + 3 números)
  - Motos:                         ABC12D  (3 letras + 2 números + 1 letra)
  - Placas diplomáticas:           CD1234  (CD + 4 números) — soporte básico
"""

import re
from utils.logger import get_logger

logger = get_logger("plate_validator")

# Patrones de placas colombianas
PATTERNS = {
    "particular": re.compile(r"^[A-Z]{3}\d{3}$"),          # ABC123
    "moto":       re.compile(r"^[A-Z]{3}\d{2}[A-Z]$"),     # ABC12D
    "diplomatica": re.compile(r"^CD\d{4}$"),                # CD1234
}

def _corregir_ocr(text):
    """
    Corrige errores típicos de OCR en placas colombianas.
    Formato: 3 letras + 3 caracteres
    - Posiciones 0,1,2 → solo letras (O→0 al revés, 0→O)
    - Posiciones 3,4   → solo números (O→0, I→1, L→1, S→5, B→8)
    - Posición 5       → letra (en motos) o número (particular)
    """
    if len(text) != 6:
        return text

    letras = {'0':'O', '1':'I', '5':'S', '8':'B'}
    numeros = {'O':'0', 'I':'1', 'L':'1', 'S':'5', 'B':'8', 'G':'6', 'Z':'2'}

    result = list(text)

    # Posiciones 0,1,2 deben ser letras
    for i in range(3):
        if result[i] in letras:
            result[i] = letras[result[i]]

    # Posiciones 3,4 deben ser números
    for i in range(3, 5):
        if result[i] in numeros:
            result[i] = numeros[result[i]]

    return "".join(result)

class PlateValidator:

    def validate(self, text: str):
        """
        Valida el texto OCR contra los patrones colombianos.

        Args:
            text: texto limpio (solo letras y números, mayúsculas)

        Returns:
            dict con:
                valid (bool)
                type  (str): 'particular', 'moto', 'diplomatica' o 'desconocido'
                plate (str): texto de la placa formateado (ABC 123)
        """
        text = text.strip().upper()
        text = re.sub(r"[^A-Z0-9]", "", text)
        text = _corregir_ocr(text)
        
        for plate_type, pattern in PATTERNS.items():
            if pattern.match(text):
                formatted = self._format(text, plate_type)
                logger.info(f"Placa válida: {formatted} (tipo: {plate_type})")
                return {
                    "valid": True,
                    "type": plate_type,
                    "plate": formatted,
                    "raw": text
                }

        logger.warning(f"Placa inválida o no reconocida: '{text}'")
        return {
            "valid": False,
            "type": "desconocido",
            "plate": text,
            "raw": text
        }

    @staticmethod
    def _format(text, plate_type):
        """Formatea la placa con espacio para mejor legibilidad."""
        if plate_type in ("particular", "moto"):
            return f"{text[:3]} {text[3:]}"   # ABC 123  /  ABC 12D
        return text  # diplomáticas sin cambio

    def is_valid(self, text: str) -> bool:
        """Retorna solo True/False para uso rápido."""
        return self.validate(text)["valid"]