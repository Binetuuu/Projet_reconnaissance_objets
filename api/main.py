from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from PIL import Image
import io
import logging
import time
import mlflow 
import threading
from prometheus_client import start_http_server, Counter, Histogram
import torch
import pandas as pd

# -----------------------------
# Logs
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    title="Vision API",
    description="API de détection d'objets avec YOLOv5",
    version="1.0"
)
app = FastAPI()

Instrumentator().instrument(app).expose(app)

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Métriques Prometheus
# -----------------------------
REQUEST_COUNT = Counter('request_count', 'Total API requests', ['method', 'endpoint'])
REQUEST_TIME = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])

def start_prometheus():
    start_http_server(8001)
    logger.info("Prometheus metrics serveur démarré sur le port 8001")

# -----------------------------
# Chargement du modèle YOLOv5
# -----------------------------
try:
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/yolov5s.pt', force_reload=True)
    model.eval()
    logger.info("Modèle YOLOv5 chargé avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle YOLOv5: {e}")
    raise e

# -----------------------------
# Startup event
# -----------------------------
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=start_prometheus, daemon=True).start()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()
    start_time = time.time()

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        results = model(image)

        # Traitement des résultats
        df = results.pandas().xyxy[0] if hasattr(results, 'pandas') else pd.DataFrame()
        predictions = []
        for _, row in df.iterrows():
            label = row.get("name", f"class_{int(row['class'])}")
            predictions.append({
                "xmin": float(row["xmin"]),
                "ymin": float(row["ymin"]),
                "xmax": float(row["xmax"]),
                "ymax": float(row["ymax"]),
                "confidence": float(row["confidence"]),
                "class": int(row["class"]),
                "label": label
            })

        elapsed = time.time() - start_time
        REQUEST_TIME.labels(endpoint="/predict").observe(elapsed)

        # ✅ Log dans MLflow
        with mlflow.start_run(nested=True):
            mlflow.set_tag("endpoint", "/predict")
            mlflow.log_param("filename", file.filename)
            mlflow.log_metric("response_time", elapsed)
            mlflow.log_metric("detections", len(predictions))
            mlflow.log_text(str(predictions), "results.txt")

        logger.info(f"Prédiction réussie en {elapsed:.2f}s pour {file.filename}")
        return {"predictions": predictions}

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        mlflow.set_tag("error", str(e))  # log dans MLflow si possible
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "OK", "model": "YOLOv5"}

# -----------------------------
# Serveur
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)