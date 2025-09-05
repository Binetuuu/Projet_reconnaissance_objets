FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système minimales + lib pour OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer Python deps
COPY requirements.txt .
RUN pip install --default-timeout=200 --upgrade pip -i https://pypi.org/simple \
    && pip install --default-timeout=200 --no-cache-dir -r requirements.txt -i https://pypi.org/simple


# Copier le code de l'application
COPY . .

# Lancer l'application Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
