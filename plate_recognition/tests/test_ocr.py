"""
tests/test_ocr.py
Pruebas unitarias para el validador de placas y el pipeline OCR.

Ejecutar con:
    python -m pytest tests/test_ocr.py -v
    o simplemente:
    python tests/test_ocr.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plate_validator import PlateValidator


# ──────────────────────────────────────────────────────────────────────────────
# Tests del validador
# ──────────────────────────────────────────────────────────────────────────────

validator = PlateValidator()


def test_placa_particular_valida():
    result = validator.validate("ABC123")
    assert result["valid"] == True
    assert result["type"] == "particular"
    assert result["plate"] == "ABC 123"
    print("[OK] test_placa_particular_valida")


def test_placa_moto_valida():
    result = validator.validate("XYZ12D")
    assert result["valid"] == True
    assert result["type"] == "moto"
    assert result["plate"] == "XYZ 12D"
    print("[OK] test_placa_moto_valida")


def test_placa_diplomatica_valida():
    result = validator.validate("CD1234")
    assert result["valid"] == True
    assert result["type"] == "diplomatica"
    print("[OK] test_placa_diplomatica_valida")


def test_placa_invalida_letras_extra():
    result = validator.validate("ABCD123")
    assert result["valid"] == False
    print("[OK] test_placa_invalida_letras_extra")


def test_placa_invalida_solo_numeros():
    result = validator.validate("123456")
    assert result["valid"] == False
    print("[OK] test_placa_invalida_solo_numeros")


def test_placa_vacia():
    result = validator.validate("")
    assert result["valid"] == False
    print("[OK] test_placa_vacia")


def test_placa_con_espacios_y_guiones():
    # El validador debe limpiar espacios y caracteres extra
    result = validator.validate("A B C-1 2 3")
    assert result["valid"] == True
    assert result["plate"] == "ABC 123"
    print("[OK] test_placa_con_espacios_y_guiones")


def test_placa_minusculas():
    # Debe aceptar minúsculas y convertirlas
    result = validator.validate("abc123")
    assert result["valid"] == True
    print("[OK] test_placa_minusculas")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Ejecutando pruebas del validador de placas ===\n")
    test_placa_particular_valida()
    test_placa_moto_valida()
    test_placa_diplomatica_valida()
    test_placa_invalida_letras_extra()
    test_placa_invalida_solo_numeros()
    test_placa_vacia()
    test_placa_con_espacios_y_guiones()
    test_placa_minusculas()
    print("\n✓ Todas las pruebas pasaron correctamente.\n")