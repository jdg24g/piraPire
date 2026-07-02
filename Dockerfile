FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y habilitar unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema y Node.js para Tailwind
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Exponer el puerto
EXPOSE 8000

# Dar permisos de ejecución al script de arranque
RUN chmod +x entrypoint.sh

# El comando de inicio se define mediante el entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
