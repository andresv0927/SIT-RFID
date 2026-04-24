"""
app.py
Servidor Flask principal - SIT-RFID Backend API
"""
from flask import Flask, jsonify
from flask_cors import CORS
from database import db
from routes.vehicles   import vehicles_bp
from routes.turns      import turns_bp
from routes.detections import detections_bp
from routes.rfid       import rfid_bp

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el dashboard

# ── Registrar blueprints ───────────────────────────────────────────────────────
app.register_blueprint(vehicles_bp)
app.register_blueprint(turns_bp)
app.register_blueprint(detections_bp)
app.register_blueprint(rfid_bp)


# ── Health check ───────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"ok": True, "service": "SIT-RFID API", "version": "1.0"})


# ── Manejo de errores globales ─────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"ok": False, "error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"ok": False, "error": "Error interno del servidor"}), 500


# ── Inicio ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  SIT-RFID | Backend API")
    print("  http://localhost:5000")
    print("=" * 50)
    db.connect()
    app.run(host="0.0.0.0", port=5000, debug=True)