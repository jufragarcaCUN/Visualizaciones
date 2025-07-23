import streamlit as st
from pathlib import Path

# Estilo CSS embebido
st.markdown("""
    <style>
        .stApp > header { display: none !important; }

        .stApp {
            background-color: #007A33;
            color: white;
            font-size: 16px;
        }

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .main-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 2rem !important;
            font-weight: 900;
            color: #fff;
            text-align: center;
            padding: 40px 0;
            text-shadow: 2px 2px 12px rgba(0, 255, 0, 0.3);
        }

        .image-grid {
            display: flex;
            justify-content: center;
            gap: 50px;
            padding: 40px;
            flex-wrap: wrap;
        }

        .image-grid img {
            max-width: 600px;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 0 25px rgba(0, 255, 0, 0.6);
            background-color: white;
        }

        .stAlert {
            background-color: #333 !important;
            color: #fff !important;
            border-left: 5px solid #31A354 !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: #E0E0E0;
            padding: 1rem;
        }

        [data-testid="stSidebar"] * {
            font-size: 20px !important;
            font-weight: 100;
            color: #000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Título de la app
st.markdown('<div class="main-title">🌿 Imágenes en Dos Columnas</div>', unsafe_allow_html=True)

# Rutas a las imágenes (ajusta si es necesario)
img_path = Path("static/tu_imagen.png")

# Verificación
if not img_path.exists():
    st.error("❌ No se encontró la imagen en la ruta: static/tu_imagen.png")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.image(str(img_path), caption="Imagen 1")

    with col2:
        st.image(str(img_path), caption="Imagen 2")
