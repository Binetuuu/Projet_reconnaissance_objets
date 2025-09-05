# Utiliser Python slim
FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires pour Pillow, OpenCV, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libgl1 \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .


# Exposer le port FastAPI
EXPOSE 8000

# Lancer FastAPI avec uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
