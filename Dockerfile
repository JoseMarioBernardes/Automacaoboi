# Dockerfile

FROM python:3.11-slim

# Instalações básicas e Chrome
RUN apt-get update && apt-get install -y \
    curl unzip wget gnupg2 \
    chromium chromium-driver \
    && apt-get clean

# Variável necessária para o Chrome headless
ENV CHROME_BIN=/usr/bin/chromium

# Diretório do app
WORKDIR /app

# Copiar arquivos
COPY . /app

# Instalar dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando padrão
CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
