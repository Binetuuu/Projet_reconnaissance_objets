# import mlflow
# import mlflow.pytorch
# import argparse
# import os
# from datetime import datetime
# import time
# from ultralytics import YOLO
# from mlflow.tracking import MlflowClient

# # def wait_for_mlflow(uri, max_retries=30, sleep_interval=2):
# #     client = MlflowClient(uri)
# #     for i in range(max_retries):
# #         try:
# #             client.list_experiments()
# #             print("✅ MLflow est disponible")
# #             return True
# #         except Exception:
# #             print(f"⏳ En attente de MLflow... ({i+1}/{max_retries})")
# #             time.sleep(sleep_interval)
# #     raise ConnectionError("❌ Impossible de se connecter à MLflow")

# def parse_args():
#     parser = argparse.ArgumentParser(description="Fine-tuning YOLOv5 avec MLflow")
#     parser.add_argument("--data", type=str, required=True, help="Chemin vers data.yaml")
#     parser.add_argument("--epochs", type=int, default=20, help="Nombre d'epochs")
#     parser.add_argument("--batch-size", type=int, default=8, help="Taille du batch")
#     parser.add_argument("--img-size", type=int, default=320, help="Taille des images")
#     parser.add_argument("--mlflow-uri", type=str, default="http://mlflow:5000", help="URI MLflow")
#     return parser.parse_args()

# def main():
#     args = parse_args()

#     mlflow.set_tracking_uri(args.mlflow_uri)
#     mlflow.set_experiment("YOLOv5 Fine-Tuning")

#     with mlflow.start_run():
#         try:
#             mlflow.log_params(vars(args))

#             # Charger le modèle YOLOv5
#             model = YOLO("yolov5s.pt")

#             # # Entraînement
#             # results = model.train(
#             #     data=args.data,
#             #     epochs=args.epochs,
#             #     batch=args.batch_size,
#             #     imgsz=args.img_size,
#             #     project="models",
#             #     name=f"yolov5_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#             # )
#             # Entraînement optimisé pour faible mémoire

#             results = model.train(
#                 data=args.data,
#                 epochs=args.epochs,
#                 batch=args.batch_size,      # réduis si crash, ex: 1-2
#                 imgsz=args.img_size,        # taille réduite, ex: 320
#                 project="models",
#                 name=f"yolov5_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
#                 cache=False,   
#                 workers=0,             # désactive le cache pour économiser la RA
#                 mosaic=0.0,                 # désactiver augmentations lourdes
#                 mixup=0.0,
#                 copy_paste=0.0
#             )

            

#             metrics = model.metrics
#             m = metrics.mean_results()  # [precision, recall, mAP50, mAP50-95]
#             mlflow.log_metric("best_precision", m[0])
#             mlflow.log_metric("best_recall", m[1])
#             mlflow.log_metric("best_map", m[2])
#             mlflow.log_metric("map50_95", m[3])


#             # Sauvegarde du modèle
#             best_model_path = os.path.join(model.trainer.save_dir, "weights", "best.pt")
#             if os.path.exists(best_model_path):
#                 mlflow.log_artifact(best_model_path)
#                 print(f"✅ Modèle sauvegardé : {best_model_path}")

#             print("🎉 Entraînement terminé avec succès !")

#         except Exception as e:
#             mlflow.log_param("error", str(e))
#             raise

# if __name__ == "__main__":
#     main()
import mlflow
import mlflow.pytorch
import argparse
import os
from datetime import datetime
import time
from ultralytics import YOLO
from mlflow.tracking import MlflowClient

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tuning YOLOv5 avec MLflow")
    parser.add_argument("--data", type=str, required=True, help="Chemin vers data.yaml")
    parser.add_argument("--epochs", type=int, default=20, help="Nombre d'epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Taille du batch")
    parser.add_argument("--img-size", type=int, default=320, help="Taille des images")
    parser.add_argument("--mlflow-uri", type=str, default="http://mlflow:5000", help="URI MLflow")
    return parser.parse_args()

def main():
    args = parse_args()

    # ✅ Prendre l'URI depuis l'environnement si présent (Docker Compose)
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", args.mlflow_uri)
    print("MLflow URI:", mlflow_uri)
    mlflow.set_tracking_uri(mlflow_uri)

    # ✅ Crée l'expérience si elle n'existe pas
    mlflow.set_experiment("YOLOv5 Fine-Tuning")

    # ✅ Démarre le run MLflow
    with mlflow.start_run():
        try:
            mlflow.log_params(vars(args))

            # Charger le modèle YOLOv5
            model = YOLO("yolov5s.pt")

            # Entraînement optimisé pour faible mémoire
            results = model.train(
                data=args.data,
                epochs=args.epochs,
                batch=args.batch_size,
                imgsz=args.img_size,
                project="models",
                name=f"yolov5_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                cache=False,
                workers=0,       # faible mémoire
                mosaic=0.0,
                mixup=0.0,
                copy_paste=0.0
            )

            # ✅ Log des métriques principales
            metrics = model.metrics
            m = metrics.mean_results()  # [precision, recall, mAP50, mAP50-95]
            mlflow.log_metric("best_precision", m[0])
            mlflow.log_metric("best_recall", m[1])
            mlflow.log_metric("best_map", m[2])
            mlflow.log_metric("map50_95", m[3])

            # ✅ Sauvegarde du modèle si présent
            best_model_path = os.path.join(model.trainer.save_dir, "weights", "best.pt")
            if os.path.exists(best_model_path):
                mlflow.log_artifact(best_model_path)
                print(f"✅ Modèle sauvegardé : {best_model_path}")
            else:
                print("⚠️ Modèle best.pt non trouvé, artefact non sauvegardé")

            print("🎉 Entraînement terminé avec succès !")

        except Exception as e:
            mlflow.log_param("error", str(e))
            raise

if __name__ == "__main__":
    main()
