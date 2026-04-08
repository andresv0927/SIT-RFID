@echo off
echo ============================================
echo   SIT-RFID - Instalacion de dependencias
echo ============================================

echo.
echo [1/3] Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate

echo.
echo [2/3] Instalando paquetes Python...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [3/3] Verificando Tesseract...
where tesseract >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Tesseract NO encontrado.
    echo     Descargalo e instalalo desde:
    echo     https://github.com/UB-Mannheim/tesseract/wiki
    echo     Ruta recomendada: C:\Program Files\Tesseract-OCR\
    echo     Luego agrega esa ruta a las variables de entorno PATH.
) ELSE (
    echo [OK] Tesseract encontrado.
)

echo.
echo ============================================
echo   Instalacion completada.
echo   Para activar el entorno: venv\Scripts\activate
echo   Para ejecutar:           python plate_recognition/main.py
echo ============================================
pause