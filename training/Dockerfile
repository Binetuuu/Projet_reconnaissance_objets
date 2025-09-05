FROM python:3.10-slim

WORKDIR /app

# Installer les librairies système nécessaires
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip
RUN python -m pip install --upgrade pip

# Copier requirements
COPY requirements.txt .
RUN pip install --default-timeout=200 --upgrade pip -i https://pypi.org/simple \
    && pip install --default-timeout=200 --no-cache-dir -r requirements.txt -i https://pypi.org/simple


# Copier le code de l'application
COPY . .
