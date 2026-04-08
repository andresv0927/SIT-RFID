"""
database.py
Conexión y esquema MySQL para SIT-RFID.
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("database")

# ── Configuración ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",          
    "password": "@nDres09",          
    "database": "sit_rfid",
    "charset":  "utf8mb4",
    "autocommit": True,
}

# ── SQL de creación de tablas ──────────────────────────────────────────────────
CREATE_DB_SQL = "CREATE DATABASE IF NOT EXISTS sit_rfid CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

CREATE_VEHICLES_SQL = """
CREATE TABLE IF NOT EXISTS vehicles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    plate       VARCHAR(10)  NOT NULL UNIQUE,
    plate_type  VARCHAR(20)  NOT NULL,          -- particular | moto | diplomatica
    owner_name  VARCHAR(100) DEFAULT NULL,
    owner_doc   VARCHAR(20)  DEFAULT NULL,
    active      TINYINT(1)   DEFAULT 1,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

CREATE_TURNS_SQL = """
CREATE TABLE IF NOT EXISTS turns (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id   INT         NOT NULL,
    plate        VARCHAR(10) NOT NULL,
    turn_number  INT         NOT NULL,
    status       ENUM('waiting','attending','done','cancelled') DEFAULT 'waiting',
    score        FLOAT       DEFAULT 0,
    created_at   DATETIME    DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
) ENGINE=InnoDB;
"""

CREATE_DETECTIONS_SQL = """
CREATE TABLE IF NOT EXISTS detections (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    plate       VARCHAR(10) NOT NULL,
    confidence  FLOAT       DEFAULT 0,
    is_known    TINYINT(1)  DEFAULT 0,       -- 1 si ya estaba en vehicles
    raw_text    VARCHAR(20) DEFAULT NULL,    -- texto crudo antes de corrección
    detected_at DATETIME    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

# ── Clase de conexión ──────────────────────────────────────────────────────────
class Database:

    def __init__(self):
        self.conn = None

    def connect(self):
        try:
            # Primero crear la BD si no existe
            cfg_no_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
            tmp = mysql.connector.connect(**cfg_no_db)
            tmp.cursor().execute(CREATE_DB_SQL)
            tmp.close()

            # Conectar a la BD
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self._create_tables()
            logger.info("Conexión MySQL establecida.")
        except Error as e:
            logger.error(f"Error MySQL: {e}")
            raise

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(CREATE_VEHICLES_SQL)
        cursor.execute(CREATE_TURNS_SQL)
        cursor.execute(CREATE_DETECTIONS_SQL)
        cursor.close()

    def cursor(self):
        # Reconectar si se perdió la conexión
        if not self.conn or not self.conn.is_connected():
            self.connect()
        return self.conn.cursor(dictionary=True)

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()


# Instancia global
db = Database()