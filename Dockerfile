# Usa Python 3.13 con debian reducido para docker
FROM python:3.13-slim

#Se localiza en la carpeta app para correr la app
WORKDIR /app

#Instala la paquetería del requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./tests ./tests

#Expone puerto 8000
EXPOSE 8000

#Comando de consola para arrancar app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

