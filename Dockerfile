FROM python:3.12.6-slim

# Imposta la working directory
WORKDIR /app

ENV TERM=xterm-256color

# Copia tutto il resto del progetto
COPY ./ /app

# Installa le dipendenze Node.js e Python
# Installa curl, gnupg (per aggiungere repo Node), build-essential (utile per compilare moduli)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y nodejs \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN npm install
RUN pip install --no-cache-dir -r requirements.txt


# Comando di avvio
CMD ["python", "/app/off_chain/main.py"]
