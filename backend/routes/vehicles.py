"""
routes/vehicles.py
Endpoints para gestión de vehículos registrados.
"""
from flask import Blueprint, request, jsonify
from database import db
from utils.logger import get_logger
from datetime import datetime

logger = get_logger("vehicles")
vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/api/vehicles")


# ── GET /api/vehicles ──────────────────────────────────────────────────────────
@vehicles_bp.route("", methods=["GET"])
def list_vehicles():
    """Lista todos los vehículos registrados."""
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT v.*, 
                   COUNT(t.id) AS total_turns
            FROM vehicles v
            LEFT JOIN turns t ON t.vehicle_id = v.id
            GROUP BY v.id
            ORDER BY v.created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        # serializar fechas
        for r in rows:
            r["created_at"] = str(r["created_at"])
            r["updated_at"] = str(r["updated_at"])
        return jsonify({"ok": True, "data": rows})
    except Exception as e:
        logger.error(f"list_vehicles: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ── GET /api/vehicles/<plate> ──────────────────────────────────────────────────
@vehicles_bp.route("/<plate>", methods=["GET"])
def get_vehicle(plate):
    """Busca un vehículo por placa. Usado por el módulo OCR."""
    plate = plate.upper().replace(" ", "")
    try:
        cur = db.cursor()
        cur.execute("SELECT * FROM vehicles WHERE plate = %s", (plate,))
        row = cur.fetchone()
        cur.close()
        if row:
            row["created_at"] = str(row["created_at"])
            row["updated_at"] = str(row["updated_at"])
            return jsonify({"ok": True, "found": True,  "data": row})
        return jsonify({"ok": True, "found": False, "data": None})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── POST /api/vehicles ─────────────────────────────────────────────────────────
@vehicles_bp.route("", methods=["POST"])
def create_vehicle():
    """
    Registra un nuevo vehículo.
    Si la placa ya existe → retorna error 409 sin insertar.
    Body JSON: { plate, plate_type, owner_name?, owner_doc? }
    """
    data = request.get_json(silent=True) or {}
    plate      = (data.get("plate") or "").upper().replace(" ", "")
    plate_type = data.get("plate_type", "particular")
    owner_name = data.get("owner_name")
    owner_doc  = data.get("owner_doc")

    if not plate:
        return jsonify({"ok": False, "error": "plate requerida"}), 400

    try:
        cur = db.cursor()

        # ── Verificar duplicado ───────────────────────────────────────────────
        cur.execute("SELECT id, plate FROM vehicles WHERE plate = %s", (plate,))
        existing = cur.fetchone()
        if existing:
            cur.close()
            return jsonify({
                "ok":      False,
                "error":   "PLATE_EXISTS",
                "message": f"La placa {plate} ya está registrada.",
                "data":    existing
            }), 409  # Conflict

        # ── Insertar ──────────────────────────────────────────────────────────
        cur.execute("""
            INSERT INTO vehicles (plate, plate_type, owner_name, owner_doc)
            VALUES (%s, %s, %s, %s)
        """, (plate, plate_type, owner_name, owner_doc))
        new_id = cur.lastrowid
        cur.close()

        logger.info(f"Vehículo registrado: {plate} ({plate_type})")
        return jsonify({
            "ok":      True,
            "message": f"Vehículo {plate} registrado.",
            "id":      new_id
        }), 201

    except Exception as e:
        logger.error(f"create_vehicle: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ── PUT /api/vehicles/<plate> ──────────────────────────────────────────────────
@vehicles_bp.route("/<plate>", methods=["PUT"])
def update_vehicle(plate):
    """Actualiza datos del propietario."""
    plate = plate.upper().replace(" ", "")
    data  = request.get_json(silent=True) or {}
    try:
        cur = db.cursor()
        cur.execute("""
            UPDATE vehicles
            SET owner_name = %s, owner_doc = %s, active = %s
            WHERE plate = %s
        """, (
            data.get("owner_name"),
            data.get("owner_doc"),
            data.get("active", 1),
            plate
        ))
        cur.close()
        return jsonify({"ok": True, "message": f"{plate} actualizado."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── DELETE /api/vehicles/<plate> ───────────────────────────────────────────────
@vehicles_bp.route("/<plate>", methods=["DELETE"])
def delete_vehicle(plate):
    """Desactiva un vehículo (soft delete)."""
    plate = plate.upper().replace(" ", "")
    try:
        cur = db.cursor()
        cur.execute("UPDATE vehicles SET active = 0 WHERE plate = %s", (plate,))
        cur.close()
        return jsonify({"ok": True, "message": f"{plate} desactivado."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500