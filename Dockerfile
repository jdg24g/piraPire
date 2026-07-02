FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y habilitar unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Exponer el puerto
EXPOSE 8000

# El comando de inicio se define en docker-compose para mayor flexibilidad.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
