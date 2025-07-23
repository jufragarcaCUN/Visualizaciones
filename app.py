import streamlit as st
import base64
from pathlib import Path

# ===================================================
# 1. Configuración inicial de la página
# ===================================================
st.set_page_config(
    page_title="Desempeño llamada por asesor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================
# 2. Rutas y carga de los logos
# ===================================================
current_dir = Path(__file__).parent
logo_folder_name = "data"
logo_path1 = current_dir / logo_folder_name / "CUN-1200X1200.png"
logo_path2 = current_dir / logo_folder_name / "coe.jpeg"

def encode_image(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"❌ No se encontró la imagen: {path}")
        return ""
    except Exception as e:
        st.error(f"❌ Error al cargar imagen {path}: {e}")
        return ""

encoded_logo1 = encode_image(logo_path1)
encoded_logo2 = encode_image(logo_path2)

# ===================================================
# 3. Estilos CSS personalizados
# ===================================================
st.markdown(
    """
    <style>
        .stApp > header {
            display: none !important;
        }
        .stApp {
            background-color: #007A33;
            color: #ffffff;
            font-size: 16px;
        }
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .title-container {
            width: 100%;
            padding: 40px 0;
            margin: 0 auto;
        }
        .main-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 7rem !important;
            font-weight: 700;
            color: #31A354;
            text-align: center;
            padding: 0 50px;
            text-shadow: 2px 2px 12px rgba(0, 255, 0, 0.3);
        }
        .logo-img {
            max-width: 50px;
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
            font-weight: 600;
            color: #000 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================================================
# 4. Título principal
# ===================================================
st.markdown(
    """
    <div class="title-container">
        <p class="main-title">DESEMPEÑO LLAMADA POR ASESOR</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===================================================
# 5. Mostrar las dos imágenes en columnas
# ===================================================
if encoded_logo1 and encoded_logo2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{encoded_logo1}' class='logo-img'></div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/jpeg;base64,{encoded_logo2}' class='logo-img'></div>",
            unsafe_allow_html=True
        )
else:
    st.warning("⚠️ No se pudieron cargar una o ambas imágenes.")
