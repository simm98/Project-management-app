# Usa Python 3.13 con debian reducido para docker
FROM python:3.13-slim

# Dependencias del sistema necesarias para psycopg2 y compilación
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

#Se localiza en la carpeta app para correr la app
WORKDIR /app

COPY . .

# Copiar archivos de Poetry
COPY pyproject.toml poetry.lock README.md ./

# Instalar Poetry y dependencias
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main

#Expone puerto 8000
EXPOSE 8000

#Comando de consola para arrancar app
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

