# SIT-RFID — Reconocimiento de Placas

Sistema Inteligente de Turnos con RFID y visión artificial.

## Estructura del proyecto

```
SIT-RFID/
│
├── plate_recognition/
│   ├── main.py                  # Punto de entrada principal
│   ├── camera_capture.py        # Captura de frames desde webcam
│   ├── plate_detector.py        # Detección y recorte de la placa
│   ├── ocr_reader.py            # Lectura del texto con Tesseract
│   ├── plate_validator.py       # Validación del formato de placa colombiana
│   │
│   ├── models/                  # Modelos entrenados (Haar, YOLO, etc.)
│   ├── utils/
│   │   ├── image_utils.py       # Funciones de preprocesamiento de imagen
│   │   └── logger.py            # Logging del sistema
│   │
│   ├── data/
│   │   ├── images/              # Imágenes capturadas
│   │   └── samples/             # Imágenes de prueba
│   │
│   └── tests/
│       └── test_ocr.py          # Pruebas unitarias
│
├── requirements.txt
├── setup.bat                    # Instalación automática en Windows
└── README.md
```

## Instalación rápida (Windows)

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar Tesseract OCR
#    Descargar de: https://github.com/UB-Mannheim/tesseract/wiki
#    Instalar en: C:\Program Files\Tesseract-OCR\
```

## Flujo del módulo

```
Webcam → Frame → Detección de placa → Preprocesamiento → OCR → Validación → Resultado
```

## Formato de placas colombianas

- Vehículo particular: `ABC 123`  (3 letras + 3 números)
- Motos:              `ABC 12D`   (3 letras + 2 números + 1 letra)

# SIT-RFID — Backend API

## Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements_backend.txt
```

### 2. Configurar MySQL
Edita `database.py` y cambia:
```python
DB_CONFIG = {
    "user":     "root",
    "password": "TU_PASSWORD",   # ← cambia esto
    ...
}
```
> La base de datos `sit_rfid` y las tablas se crean automáticamente al iniciar.

### 3. Iniciar el servidor
```bash
python app.py
```
Servidor corriendo en: http://localhost:5000

---

## Estructura del backend
```
backend/
├── app.py                  ← punto de entrada Flask
├── database.py             ← conexión MySQL + esquema
├── dashboard.html          ← abrir en el navegador
├── api_client.py           ← copiar a plate_recognition/
├── requirements_backend.txt
├── routes/
│   ├── vehicles.py         ← CRUD vehículos
│   ├── turns.py            ← gestión de turnos
│   └── detections.py       ← entrada principal desde OCR
└── utils/
    └── logger.py
```

---

## Integrar con plate_recognition

1. Copia `api_client.py` a `plate_recognition/`
2. En `main.py`, dentro de `_print_result()`, agrega:

```python
from api_client import send_detection

def _print_result(result, score):
    print(f"\n{'='*45}")
    print(f"  ✅ PLACA CONFIRMADA  : {result['plate']}")
    print(f"     TIPO              : {result['type'].upper()}")
    print(f"     SCORE CONFIANZA   : {score:.0f}%")
    print(f"{'='*45}\n")

    # ← Enviar al backend
    resp = send_detection(
        plate=result['plate'],
        plate_type=result['type'],
        confidence=score
    )
    if resp.get("already_registered"):
        print(f"  ⚠️  YA REGISTRADA — no se duplicó en BD")
    elif resp.get("turn_number"):
        print(f"  🎫 Turno #{resp['turn_number']} asignado")
```

---

## Endpoints disponibles

| Método | URL                        | Descripción                        |
|--------|----------------------------|------------------------------------|
| GET    | /api/health                | Estado del servidor                |
| POST   | /api/detect                | Recibe detección OCR ← principal   |
| GET    | /api/detect/recent         | Últimas 20 detecciones             |
| GET    | /api/vehicles              | Lista vehículos                    |
| GET    | /api/vehicles/:plate       | Busca por placa                    |
| POST   | /api/vehicles              | Registra vehículo                  |
| PUT    | /api/vehicles/:plate       | Actualiza propietario              |
| DELETE | /api/vehicles/:plate       | Desactiva vehículo                 |
| GET    | /api/turns                 | Turnos del día                     |
| GET    | /api/turns/stats           | Estadísticas del día               |
| POST   | /api/turns                 | Crea turno manualmente             |
| PATCH  | /api/turns/:id/status      | Cambia estado del turno            |

---

## Lógica de placa duplicada

```
OCR detecta placa
       │
       ▼
POST /api/detect
       │
       ├─ ¿Ya existe en vehicles? ──► SÍ ──► already_registered: true
       │                                      No inserta nada
       │                                      Dashboard muestra ⚠️
       │
       └─ NO ──► Inserta en vehicles
                 Asigna número de turno
                 Dashboard muestra ✅ + turno
```