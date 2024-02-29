FROM --platform=linux/amd64 python:3.11.7-slim-bullseye

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual al directorio de trabajo
COPY . .

# Install make
RUN apt update && apt install -y --no-install-recommends \
    make \
    libgl1 \
    libglib2.0-0

# Expone el puerto 5000 (puedes cambiarlo según las necesidades de tu aplicación)
EXPOSE 8000

# Instala todas las dependencias
RUN make dependencies

ARG env_arg=dev
ENV env=$env_arg

# Comando para ejecutar la aplicación
CMD make lunch