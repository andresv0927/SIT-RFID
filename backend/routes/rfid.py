"""
routes/rfid.py
Endpoints para gestión de tags RFID.
"""
from flask import Blueprint, request, jsonify
from database import db
from utils.logger import get_logger

logger = get_logger("rfid")
rfid_bp = Blueprint("rfid", __name__, url_prefix="/api/rfid")


@rfid_bp.route("/scan", methods=["POST"])
def scan():
    data = request.get_json(silent=True) or {}
    uid  = (data.get("uid") or "").upper().strip()
    if not uid:
        return jsonify({"ok": False, "error": "uid requerido"}), 400
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT r.*, v.owner_name, v.plate_type, v.active as vehicle_active
            FROM rfid_tags r
            JOIN vehicles v ON v.id = r.vehicle_id
            WHERE r.uid = %s AND r.active = 1
        """, (uid,))
        tag = cur.fetchone()
        cur.close()
        if not tag:
            return jsonify({"ok":True,"authorized":False,"message":"Tag no registrado","uid":uid})
        if not tag["vehicle_active"]:
            return jsonify({"ok":True,"authorized":False,"message":"Vehículo inactivo","uid":uid,"plate":tag["plate"]})
        return jsonify({"ok":True,"authorized":True,"message":f"Acceso autorizado — {tag['plate']}",
                        "uid":uid,"plate":tag["plate"],"owner_name":tag["owner_name"],"plate_type":tag["plate_type"]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@rfid_bp.route("", methods=["GET"])
def list_tags():
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT r.*, v.owner_name FROM rfid_tags r
            JOIN vehicles v ON v.id = r.vehicle_id
            ORDER BY r.created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        for r in rows:
            r["created_at"] = str(r["created_at"])
        return jsonify({"ok": True, "data": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@rfid_bp.route("/register", methods=["POST"])
def register():
    data  = request.get_json(silent=True) or {}
    uid   = (data.get("uid") or "").upper().strip()
    plate = (data.get("plate") or "").upper().strip()
    if not uid or not plate:
        return jsonify({"ok": False, "error": "uid y plate requeridos"}), 400
    try:
        cur = db.cursor()
        cur.execute("SELECT id FROM vehicles WHERE plate = %s AND active = 1", (plate,))
        vehicle = cur.fetchone()
        if not vehicle:
            cur.close()
            return jsonify({"ok": False, "error": "Placa no encontrada"}), 404
        cur.execute("""
            INSERT INTO rfid_tags (uid, vehicle_id, plate)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE vehicle_id = %s, plate = %s, active = 1
        """, (uid, vehicle["id"], plate, vehicle["id"], plate))
        cur.close()
        return jsonify({"ok":True,"message":f"Tag {uid} asociado a {plate}"}), 201
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@rfid_bp.route("/<uid>", methods=["DELETE"])
def delete_tag(uid):
    try:
        cur = db.cursor()
        cur.execute("UPDATE rfid_tags SET active = 0 WHERE uid = %s", (uid.upper(),))
        cur.close()
        return jsonify({"ok": True, "message": f"Tag {uid} desactivado."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500