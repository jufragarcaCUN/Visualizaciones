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
# 2. Rutas y carga del logo
# ===================================================
current_dir = Path(__file__).parent
logo_folder_name = "data"
logo_path = current_dir / logo_folder_name / "CUN-1200X1200.png"

encoded_logo = ""
try:
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
except FileNotFoundError:
    st.error(f"Error: El archivo del logo NO SE ENCONTRÓ en la ruta: {logo_path}.")
except Exception as e:
    st.error(f"Error al cargar la imagen del logo: {e}")

# ===================================================
# 3. Estilos CSS personalizados
# ===================================================
st.markdown(
    f"""
    <style>
        .stApp > header {{
            display: none !important;
        }}
        .stApp {{
            background-color: #007A33;
            color: #ffffff;
            font-size: 16px;
        }}
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        .title-container {{
            width: 100%;
            background-color: transparent;
            padding: 40px 0;
            margin: 0 auto;
        }}
        .main-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 7rem !important;
            font-weight: 700;
            color: #31A354;
            text-align: center;
            margin: 0;
            padding: 0 50px;
            width: 100%;
            display: block;
            text-shadow: 2px 2px 12px rgba(0, 255, 0, 0.3);
            box-sizing: border-box;
        }}
        .sub-title {{
            font-size: 2.5rem;
            color: #90EE90;
            margin-bottom: 1.5em;
            font-style: italic;
        }}
        .logo-img {{
            max-width: 100px;
            height: auto;
            border-radius: 15px;
            box-shadow: 0 0 25px rgba(0, 255, 0, 0.6);
            background-color: white;
        }}
        .stAlert {{
            background-color: #333333 !important;
            color: #ffffff !important;
            border-left: 5px solid #31A354 !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background-color: #E0E0E0;
            padding: 1rem;
        }}
        [data-testid="stSidebar"] * {{
            font-size: 20px !important;
            font-weight: 600;
            color: #000000 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================================================
# 4. Título principal
# ===================================================
st.markdown(
    f"""
    <div class="title-container">
        <p class="main-title">DESEMPEÑO LLAMADA POR ASESOR</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===================================================
# 5. Mostrar dos imágenes en columnas
# ===================================================
if encoded_logo:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{encoded_logo}' class='logo-img'></div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{encoded_logo}' class='logo-img'></div>",
            unsafe_allow_html=True
        )
else:
    st.warning("⚠️ No se pudo cargar el logo.")
