import streamlit as st
import base64
from pathlib import Path

# ===================================================
# 1. Configuración inicial de la página
# ===================================================
st.set_page_config(
    page_title="Bienvenido a CUN",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded" # ¡Asegura que la barra lateral esté visible!
)

# ===================================================
# 2. Rutas y carga del logo
# ===================================================
current_dir = Path(__file__).parent # Obtiene la carpeta donde está app.py
logo_folder_name = "data" # Tu carpeta con el logo
logo_path = current_dir / logo_folder_name / "CUN-1200X1200.png" # Ruta al logo

encoded_logo = ""
try:
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
except FileNotFoundError:
    st.error(f"Error: El archivo del logo NO SE ENCONTRÓ en la ruta: {logo_path}. Por favor, verifica la ruta y el nombre del archivo.")
except Exception as e:
    st.error(f"Error al cargar la imagen del logo: {e}")

# ===================================================
# 3. Estilos CSS personalizados para la interfaz
# ===================================================
st.markdown(
    f"""
    <style>
    /* Ocultar el botón de menú de Streamlit */
    .stApp > header {{
        display: none !important;
    }}

    /* Fondo negro para toda la aplicación */
    .stApp {{
        background-color: #000000; 
        color: #ffffff; /* Color de texto blanco por defecto */
    }}

    /* Ajuste para el contenido principal (para que no ocupe todo el ancho si hay sidebar) */
    .main .block-container {{
        max-width: 1200px; /* Ancho máximo para el contenido principal */
        padding-left: 1rem;
        padding-right: 1rem;
    }}

    /* Contenedor del logo y texto para centrarlo en la pantalla de bienvenida */
    .content-wrapper {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 20px;
        max-width: 800px; /* Limita el ancho del contenido si es necesario */
        margin: auto; /* Centra el wrapper */
        height: 100vh; /* Ocupa toda la altura disponible para centrar verticalmente */
    }}

    .main-title {{
        font-size: 3.5em; /* Tamaño grande para el título principal */
        font-weight: bold;
        color: #31A354; /* Un verde vibrante para el título */
        margin-bottom: 0.2em;
        text-shadow: 2px 2px 8px rgba(0, 255, 0, 0.4); /* Sombra sutil verde */
    }}

    .sub-title {{
        font-size: 1.5em; /* Tamaño para el subtítulo */
        color: #90EE90; /* Un verde claro para el subtítulo */
        margin-bottom: 1.5em;
        font-style: italic;
    }}

    .logo-img {{
        max-width: 280px; /* Tamaño del logo. Puedes ajustar esto */
        height: auto;
        border-radius: 15px; /* Bordes ligeramente redondeados para el logo */
        box-shadow: 0 0 25px rgba(0, 255, 0, 0.6); /* Sombra que brilla en verde */
        animation: pulse 2s infinite alternate; /* Animación de pulsación sutil */
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); box-shadow: 0 0 15px rgba(0, 255, 0, 0.4); }}
        100% {{ transform: scale(1.05); box-shadow: 0 0 30px rgba(0, 255, 0, 0.8); }}
    }}

    /* Ajustes para los st.error y st.info para que contrasten */
    .stAlert {{
        background-color: #333333 !important; /* Fondo gris oscuro para alertas */
        color: #ffffff !important; /* Texto blanco para alertas */
        border-left: 5px solid #31A354 !important; /* Borde verde */
    }}

    /* AJUSTE CLAVE: Fondo de la barra lateral (sidebar) */
    [data-testid="stSidebar"] {{
        background-color: #E0E0E0; /* ¡GRIS CLARO PARA EL SIDEBAR! */
        color: #000000; /* Texto oscuro para que contraste en el sidebar */
    }}
    /* Puedes añadir más estilos para elementos específicos del sidebar si los añades después */
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================================================
# 4. Contenido de la página (Bienvenida y Logo)
# ===================================================

# Esta sección se centra en la pantalla
st.markdown(
    f"""
    <div class="content-wrapper">
        <p class="main-title">BIENVENIDO A CUN</p>
        <p class="sub-title">Corporación Unificada Nacional de Educación Superior</p>
        {"<img src='data:image/png;base64," + encoded_logo + "' class='logo-img'>" if encoded_logo else ""}
    </div>
    """,
    unsafe_allow_html=True,
)

# ===================================================
# 5. Contenido del Sidebar (Ejemplo)
# ===================================================
# Si solo quieres ver la barra lateral, puedes poner algo simple aquí
with st.sidebar:
    st.header("Este es el Sidebar")
    st.write("¡Aquí puedes poner contenido futuro si lo necesitas!")
    st.button("Un Botón de Ejemplo")
    st.checkbox("Una Opción de Ejemplo")