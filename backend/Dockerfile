FROM python:3.11-slim

WORKDIR /app

COPY requirements_backend.txt .
RUN pip install --no-cache-dir -r requirements_backend.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]