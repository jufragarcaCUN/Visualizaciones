import streamlit as st
import base64
from pathlib import Path

# ================== 1. CONFIGURACIÓN DE PÁGINA ==================
st.set_page_config(
    page_title="Desempeño llamada por asesor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== 2. CARGA DEL LOGO ==================
logo_path = Path(__file__).parent / "data" / "CUN-1200X1200.png"

encoded_logo = ""
if logo_path.exists():
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
else:
    st.warning(f"⚠️ Logo no encontrado en: {logo_path}")

# ================== 3. ESTILOS CSS PERSONALIZADOS ==================
st.markdown(f"""
<style>
    .stApp > header {{ display: none !important; }}
    .stApp {{
        background-color: #007A33;
        color: white;
        font-size: 16px;
    }}
    .main .block-container {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}
    .main-title {{
        font-family: 'Montserrat', sans-serif;
        font-size: 2rem !important;
        font-weight: 900;
        color: #fff;
        text-align: center;
        padding: 40px 0;
        text-shadow: 2px 2px 12px rgba(0, 255, 0, 0.3);
    }}
    .image-container {{
        text-align: center;
        padding: 50px;
    }}
    .logo-img {{
        max-width: 600px !important; /* ¡Modificación clave aquí! */
        height: auto;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(0, 255, 0, 0.6);
        background-color: white;
    }}
    .stAlert {{
        background-color: #333 !important;
        color: #fff !important;
        border-left: 5px solid #31A354 !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background-color: #E0E0E0;
        padding: 1rem;
    }}
    [data-testid="stSidebar"] * {{
        font-size: 20px !important;
        font-weight: 100;
        color: #000 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ================== 4. CONTENIDO PRINCIPAL ==================
st.markdown('<div class="main-title">DESEMPEÑO LLAMADA POR ASESOR</div>', unsafe_allow_html=True)

if encoded_logo:
    st.markdown(f"""
        <div class="image-container">
            <img src='data:image/png;base64,{encoded_logo}' class='logo-img'>
        </div>
    """, unsafe_allow_html=True)
