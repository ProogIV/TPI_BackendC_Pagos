# Microservicio Backend C - Pagos (Python + FastAPI)
FROM python:3.11-slim

WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de FastAPI
COPY . .

# Puerto expuesto para la API de pagos
EXPOSE 8001

ENV PYTHONUNBUFFERED=1

# Ejecución con servidor Uvicorn en modo producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
