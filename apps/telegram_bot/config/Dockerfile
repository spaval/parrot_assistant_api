FROM --platform=linux/amd64 python:3.11.7

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido actual al directorio de trabajo
COPY . .

# Instala todas las dependencias
RUN make dependencies

ARG env_arg=dev
ENV env=$env_arg

# Comando para ejecutar la aplicación
CMD make lunch