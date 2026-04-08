"""
api_client.py
Conector del módulo plate_recognition → Backend Flask.
Colocar este archivo en: plate_recognition/api_client.py
"""
import requests
from utils.logger import get_logger

logger = get_logger("api_client")

API_URL = "http://localhost:5000/api"
TIMEOUT = 3  # segundos


def send_detection(plate: str, plate_type: str, confidence: float, raw_text: str = "") -> dict:
    """
    Envía una placa confirmada al backend.

    Retorna:
      {
        ok: bool,
        already_registered: bool,
        message: str,
        turn_number: int | None
      }
    """
    try:
        r = requests.post(
            f"{API_URL}/detect",
            json={
                "plate":      plate,
                "plate_type": plate_type,
                "confidence": confidence,
                "raw_text":   raw_text or plate,
            },
            timeout=TIMEOUT
        )
        data = r.json()

        if data.get("already_registered"):
            logger.warning(f"Placa ya registrada: {plate}")
        else:
            logger.info(f"Placa nueva registrada: {plate} → turno #{data.get('turn_number')}")

        return data

    except requests.exceptions.ConnectionError:
        logger.warning("Backend no disponible (ConnectionError)")
        return {"ok": False, "error": "Backend offline", "already_registered": False}
    except Exception as e:
        logger.error(f"send_detection error: {e}")
        return {"ok": False, "error": str(e), "already_registered": False}