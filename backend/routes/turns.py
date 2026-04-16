"""
routes/turns.py
Endpoints para gestión de turnos.
"""
from flask import Blueprint, request, jsonify
from database import db
from utils.logger import get_logger

logger = get_logger("turns")
turns_bp = Blueprint("turns", __name__, url_prefix="/api/turns")


def _next_turn_number():
    """Obtiene el siguiente número de turno del día."""
    cur = db.cursor()
    cur.execute("""
        SELECT COALESCE(MAX(turn_number), 0) + 1 AS next_num
        FROM turns
        WHERE DATE(created_at) = CURDATE()
    """)
    row = cur.fetchone()
    cur.close()
    return row["next_num"] if row else 1


# ── GET /api/turns ─────────────────────────────────────────────────────────────
@turns_bp.route("", methods=["GET"])
def list_turns():
    """Lista turnos del día actual con estado."""
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT t.*, v.owner_name, v.plate_type
            FROM turns t
            LEFT JOIN vehicles v ON v.id = t.vehicle_id
            WHERE DATE(t.created_at) = CURDATE()
            ORDER BY t.turn_number ASC
        """)
        rows = cur.fetchall()
        cur.close()
        for r in rows:
            r["created_at"] = str(r["created_at"])
            r["updated_at"] = str(r["updated_at"])
        return jsonify({"ok": True, "data": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── GET /api/turns/stats ────────────────────────────────────────────────────────
@turns_bp.route("/stats", methods=["GET"])
def turn_stats():
    """Estadísticas del día para el dashboard."""
    try:
        cur = db.cursor()
        cur.execute("""
    SELECT
        COUNT(*)                                        AS total,
        COALESCE(SUM(status = 'waiting'), 0)            AS waiting,
        COALESCE(SUM(status = 'attending'), 0)          AS attending,
        COALESCE(SUM(status = 'done'), 0)               AS done,
        COALESCE(SUM(status = 'cancelled'), 0)          AS cancelled
    FROM turns
    WHERE DATE(created_at) = CURDATE()
""")
        stats = cur.fetchone()
        cur.close()
        return jsonify({"ok": True, "data": stats})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── POST /api/turns ────────────────────────────────────────────────────────────
@turns_bp.route("", methods=["POST"])
def create_turn():
    """
    Crea un turno para una placa detectada.
    - Si la placa NO está registrada → registra el vehículo y crea turno.
    - Si la placa YA tiene turno ACTIVO hoy → retorna 409 sin duplicar.
    Body JSON: { plate, plate_type?, score? }
    """
    data       = request.get_json(silent=True) or {}
    plate      = (data.get("plate") or "").upper().replace(" ", "")
    plate_type = data.get("plate_type", "particular")
    score      = data.get("score", 0)

    if not plate:
        return jsonify({"ok": False, "error": "plate requerida"}), 400

    try:
        cur = db.cursor()

        # 1. Buscar vehículo
        cur.execute("SELECT * FROM vehicles WHERE plate = %s", (plate,))
        vehicle = cur.fetchone()

        # 2. Si no existe → registrar automáticamente
        if not vehicle:
            cur.execute("""
                INSERT INTO vehicles (plate, plate_type)
                VALUES (%s, %s)
            """, (plate, plate_type))
            vehicle_id   = cur.lastrowid
            is_new       = True
            already_registered = False
        else:
            vehicle_id   = vehicle["id"]
            is_new       = False
            already_registered = True  # ← YA ESTABA en la BD

        # 3. Verificar turno activo hoy
        cur.execute("""
            SELECT id, turn_number, status
            FROM turns
            WHERE vehicle_id = %s
              AND DATE(created_at) = CURDATE()
              AND status IN ('waiting', 'attending')
        """, (vehicle_id,))
        active_turn = cur.fetchone()

        if active_turn:
            cur.close()
            return jsonify({
                "ok":                False,
                "error":             "TURN_EXISTS",
                "message":           f"La placa {plate} ya tiene el turno #{active_turn['turn_number']} activo.",
                "already_registered": already_registered,
                "turn":              active_turn
            }), 409

        # 4. Crear turno
        turn_number = _next_turn_number()
        cur.execute("""
            INSERT INTO turns (vehicle_id, plate, turn_number, score)
            VALUES (%s, %s, %s, %s)
        """, (vehicle_id, plate, turn_number, score))
        turn_id = cur.lastrowid
        cur.close()

        logger.info(f"Turno #{turn_number} creado para {plate}")
        return jsonify({
            "ok":                True,
            "message":           f"Turno #{turn_number} asignado a {plate}.",
            "already_registered": already_registered,
            "turn_number":       turn_number,
            "turn_id":           turn_id,
            "is_new_vehicle":    is_new
        }), 201

    except Exception as e:
        logger.error(f"create_turn: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ── PATCH /api/turns/<id>/status ───────────────────────────────────────────────
@turns_bp.route("/<int:turn_id>/status", methods=["PATCH"])
def update_turn_status(turn_id):
    """
    Cambia el estado de un turno.
    Body JSON: { status: 'waiting'|'attending'|'done'|'cancelled' }
    """
    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    valid  = ("waiting", "attending", "done", "cancelled")

    if status not in valid:
        return jsonify({"ok": False, "error": f"status debe ser uno de {valid}"}), 400

    try:
        cur = db.cursor()
        cur.execute("UPDATE turns SET status = %s WHERE id = %s", (status, turn_id))
        cur.close()
        return jsonify({"ok": True, "message": f"Turno {turn_id} → {status}."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500