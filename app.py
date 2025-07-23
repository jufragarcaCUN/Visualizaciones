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
# 2. Rutas y carga de los logos y la imagen de fondo
# ===================================================
current_dir = Path(__file__).parent
logo_folder_name = "data"
logo_path1 = current_dir / logo_folder_name / "CUN-1200X1200.png"
# Se eliminó la carga de logo_path2 = current_dir / logo_folder_name / "coe.jpeg"
# La ruta de tu imagen de fondo ahora es 'tablero4.jpg'
background_image_path = current_dir / logo_folder_name / "tablero4.jpg" 

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
# Se eliminó encoded_logo2 = encode_image(logo_path2)
encoded_background_image = encode_image(background_image_path) # Codifica la imagen de fondo

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
            /* Se eliminó background-color: #007A33; para que la imagen de fondo sea la única visible */
            color: #ff;
            font-size: 16px;
            {'background-image: url(data:image/jpeg;base64,' + encoded_background_image + ');' if encoded_background_image else ''}
            background-size: cover; /* Ajusta la imagen para cubrir todo el contenedor */
            background-repeat: no-repeat; /* Evita que la imagen se repita */
            background-attachment: fixed; /* Mantiene la imagen fija al hacer scroll */
            background-position: center center; /* Centra la imagen */
        }}
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            background-color: rgba(255, 255, 255, 0.7); /* Fondo semi-transparente para que el contenido sea legible sobre la imagen */
            border-radius: 10px;
            padding: 20px;
        }}
        .title-container {{
            width: 100%;
            padding: 40px 0;
            margin: 0 auto;
        }}
        .main-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 7rem !important;
            font-weight: 700;
            color: #31A354;
            text-align: center;
            padding: 0 50px;
            text-shadow: 2px 2px 12px rgba(0, 255, 0, 0.3);
        }}
            .logo-img {{
            width: 200px; /* o el tamaño que desees */
            height: 200px;
            object-fit: contain; /* para que mantenga la proporción */
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
            font-weight: 600;
            color: #000 !important;
        }}
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
# 5. Mostrar la imagen en una sola columna
# ===================================================
if encoded_logo1: # La condición ahora solo verifica el primer logo
    col1 = st.columns(1) # Se define una sola columna
    with col1:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{encoded_logo1}' class='logo-img'></div>",
            unsafe_allow_html=True
        )
else:
    st.warning("⚠️ No se pudo cargar la imagen del logo.")

# Contenido de tu aplicación iría aquí
st.write("¡Bienvenido a la aplicación de desempeño de llamadas!")
st.write("Aquí puedes agregar todos los elementos de tu interfaz, como gráficos, tablas, selectores, etc.")
