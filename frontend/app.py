import streamlit as st
import requests
from PIL import Image
import io
import numpy as np
import cv2
import time
import os

# Configuration de la page
st.set_page_config(
    page_title="Vision AI",
    page_icon="🖼️",
    layout="wide"
)

# CSS local (optionnel)
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Décommenter si tu as un fichier CSS
# local_css("assets/style.css")

# Header
st.title("Vision AI")
st.markdown("Détection d'objet en temps réel avec YOLOv5")

# Liste des classes pour affichage
CLASS_NAMES = ['chaise', 'chat', 'chien', 'oiseau', 'tigre', 'velo', 'voiture']

# Fonction pour dessiner les bounding boxes
def draw_boxes(image, predictions):
    img = np.array(image)
    for obj in predictions:
        x1, y1, x2, y2 = map(int, [obj['xmin'], obj['ymin'], obj['xmax'], obj['ymax']])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{obj.get('label', obj.get('name','objet'))} {obj['confidence']:.2f}"
        cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return img

# URL de l'API (variable d'environnement)
API_URL = os.environ.get("API_URL", "http://localhost:8002")

# Upload de l'image
uploaded_file = st.file_uploader("Téléversez une image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    # Affichage image originale
    with col1:
        st.subheader("Image originale")
        st.image(image, use_column_width=True)
    
    # Bouton de prédiction
    if st.button("Détecter les objets"):
        with st.spinner("Analyse en cours..."):
            # Préparer l'image pour l'API
            bytes_img = io.BytesIO()
            image.save(bytes_img, format="PNG")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{API_URL}/predict",  # <-- utilisation de la variable API_URL
                    files={"file": ("image.png", bytes_img.getvalue(), "image/png")}
                )
            
                response.raise_for_status()
                data = response.json()
                predictions = data.get("predictions", [])

                # Optionnel : ajouter 'name' depuis CLASS_NAMES si besoin
                for obj in predictions:
                    class_id = obj.get("class", 0)
                    obj["name"] = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else obj.get("label","objet")

                # Affichage résultats
                with col2:
                    st.subheader("Résultats")
                    result_img = draw_boxes(image, predictions)
                    st.image(result_img, use_column_width=True)
                    
                    with st.expander("📊 Détails"):
                        for i, obj in enumerate(predictions, 1):
                            st.write(f"**Objet {i}**: {obj.get('label', obj.get('name','?'))} (confiance: {obj['confidence']:.2%})")
                
                st.success(f"Analyse terminée en {time.time()-start_time:.2f}s")

            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de communication avec l'API: {str(e)}")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
