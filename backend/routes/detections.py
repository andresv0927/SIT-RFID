"""
routes/detections.py
Endpoint que recibe la placa detectada por el módulo OCR.
Es el punto de entrada principal desde plate_recognition/main.py
"""
from flask import Blueprint, request, jsonify
from database import db
from utils.logger import get_logger

logger = get_logger("detections")
detections_bp = Blueprint("detections", __name__, url_prefix="/api/detect")


# ── POST /api/detect ───────────────────────────────────────────────────────────
@detections_bp.route("", methods=["POST"])
def detect():
    """
    Recibe una detección del módulo OCR.
    Lógica:
      1. Registra la detección en la tabla detections.
      2. Verifica si la placa ya existe en vehicles.
         - SI existe  → retorna already_registered=True, NO crea turno automático.
         - NO existe  → crea vehículo + turno automáticamente.
      3. El dashboard muestra el resultado en tiempo real.

    Body JSON:
      { plate, plate_type, confidence, raw_text? }

    Response:
      { ok, already_registered, message, turn_number?, vehicle_id }
    """
    data       = request.get_json(silent=True) or {}
    plate      = (data.get("plate") or "").upper().replace(" ", "")
    plate_type = data.get("plate_type", "particular")
    confidence = float(data.get("confidence", 0))
    raw_text   = data.get("raw_text", plate)

    if not plate:
        return jsonify({"ok": False, "error": "plate requerida"}), 400

    try:
        cur = db.cursor()

        # ── 1. Verificar si ya está registrada ────────────────────────────────
        cur.execute("SELECT id, plate_type, owner_name FROM vehicles WHERE plate = %s", (plate,))
        vehicle = cur.fetchone()
        already_registered = vehicle is not None

        # ── 2. Registrar detección ────────────────────────────────────────────
        cur.execute("""
            INSERT INTO detections (plate, confidence, is_known, raw_text)
            VALUES (%s, %s, %s, %s)
        """, (plate, confidence, 1 if already_registered else 0, raw_text))

        # ── 3. Si ya existe → NO agregar, avisar al dashboard ─────────────────
        if already_registered:
            # Verificar si tiene turno activo
            cur.execute("""
                SELECT turn_number, status FROM turns
                WHERE vehicle_id = %s
                  AND DATE(created_at) = CURDATE()
                  AND status IN ('waiting','attending')
            """, (vehicle["id"],))
            active = cur.fetchone()
            cur.close()

            return jsonify({
                "ok":                True,
                "already_registered": True,
                "message":           f"⚠️ La placa {plate} ya está registrada.",
                "vehicle":           vehicle,
                "active_turn":       active
            })

        # ── 4. Si es nueva → registrar vehículo y crear turno ─────────────────
        cur.execute("""
            INSERT INTO vehicles (plate, plate_type)
            VALUES (%s, %s)
        """, (plate, plate_type))
        vehicle_id = cur.lastrowid

        # Número de turno del día
        cur.execute("""
            SELECT COALESCE(MAX(turn_number), 0) + 1 AS next_num
            FROM turns WHERE DATE(created_at) = CURDATE()
        """)
        turn_number = cur.fetchone()["next_num"]

        cur.execute("""
            INSERT INTO turns (vehicle_id, plate, turn_number, score)
            VALUES (%s, %s, %s, %s)
        """, (vehicle_id, plate, turn_number, confidence))
        cur.close()

        logger.info(f"Nueva placa detectada y registrada: {plate} → turno #{turn_number}")
        return jsonify({
            "ok":                True,
            "already_registered": False,
            "message":           f"✅ Placa {plate} registrada. Turno #{turn_number} asignado.",
            "turn_number":       turn_number,
            "vehicle_id":        vehicle_id
        }), 201

    except Exception as e:
        logger.error(f"detect: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ── GET /api/detect/recent ─────────────────────────────────────────────────────
@detections_bp.route("/recent", methods=["GET"])
def recent_detections():
    """Últimas 20 detecciones para el dashboard en tiempo real."""
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT * FROM detections
            ORDER BY detected_at DESC
            LIMIT 20
        """)
        rows = cur.fetchall()
        cur.close()
        for r in rows:
            r["detected_at"] = str(r["detected_at"])
        return jsonify({"ok": True, "data": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500