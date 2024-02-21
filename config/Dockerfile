FROM --platform=linux/amd64 python:3.11.7

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual al directorio de trabajo
COPY . .

# Crea un entorno virtual en /venv
RUN python3 -m venv /venv

# Establece el entorno virtual como activo
ENV PATH="/venv/bin:$PATH"

# Instala las dependencias del proyecto
RUN make deps

# Expone el puerto 5000 (puedes cambiarlo según las necesidades de tu aplicación)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD make run && make telegram