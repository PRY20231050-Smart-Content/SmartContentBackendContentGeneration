# Utiliza una imagen base de Python
FROM python:3.8

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala NLTK y descarga los recursos
RUN pip install nltk && \
    python -m nltk.downloader punkt wordnet

# Copia el archivo requirements.txt (donde se especifican las dependencias) al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install -r requirements.txt

# Copia todo el contenido de tu proyecto al contenedor
COPY . .

# Define la variable de entorno para Django (ajusta la configuración según tu proyecto)
ENV DJANGO_SETTINGS_MODULE=SmartContentBackendContentGeneration.settings

# Ejecuta la migración de la base de datos (ajusta según tu proyecto)
RUN python3 manage.py migrate

# Expone el puerto en el que se ejecuta tu aplicación Django
EXPOSE 8000

# Inicia la aplicación Django cuando se inicia el contenedor
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
