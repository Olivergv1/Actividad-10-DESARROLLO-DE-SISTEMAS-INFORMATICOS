# Usar una imagen base de Python
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para las librerías de Python
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    libxml2-dev \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /APP_2

# Copiar el archivo de requerimientos
COPY requirements.txt /APP_2//

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto al contenedor
COPY . /APP_2/

# Exponer el puerto donde se ejecutará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "aplicacion.py"]
