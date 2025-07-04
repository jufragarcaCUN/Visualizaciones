# ===================================================
# PASO 1: Importación de librerías necesarias
# ===================================================
import pandas as pd
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime

# ===================================================
# PASO 2: Configuración inicial de la app
# ===================================================
st.set_page_config(layout="wide")

# ===================================================
# PASO 3: Carga y preprocesamiento del archivo principal
# ===================================================
carpeta_base = Path(__file__).parent.parent / "data"
archivo_principal = carpeta_base / "final_servicio_cltiene.xlsx"

try:
    df = pd.read_excel(archivo_principal)
    st.success(f"✅ Archivo '{archivo_principal.name}' cargado correctamente.")
except FileNotFoundError:
    st.error(f"❌ Error: El archivo no se encontró en la ruta especificada: **{archivo_principal}**")
    st.warning("Asegúrate de que el archivo 'final_servicio_cltiene.xlsx' esté en la carpeta 'data'.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar el archivo Excel: {e}")
    st.stop()

# Verificación de columnas
st.write("🔍 Columnas detectadas:", df.columns.tolist())

# Conversión de fechas
if 'Fecha' in df.columns:
    df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
    if df['fecha_convertida'].isnull().sum() > 0:
        st.warning(f"⚠️ {df['fecha_convertida'].isnull().sum()} fechas inválidas en 'Fecha'.")
else:
    st.error("❌ La columna 'Fecha' no existe en el archivo.")

# Conversión a texto de 'Agente'
if 'Agente' in df.columns:
    df['Agente'] = df['Agente'].astype(str)
else:
    st.error("❌ La columna 'Agente' no existe en el archivo.")

# Conversión de columnas numéricas
columnas_numericas = ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity', 'Palabras', 'Oraciones']
for col in columnas_numericas:
    if col in df.columns:
        if col == 'Puntaje_Total_%' and df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if df[col].isnull().sum() > 0:
            st.warning(f"⚠️ {df[col].isnull().sum()} valores nulos en '{col}' tras conversión numérica.")
    else:
        st.warning(f"⚠️ La columna '{col}' no se encontró.")

# Búsqueda de categorías en columnas si fuera necesario
# Ejemplo: categorizar si hay columnas de texto libre para clasificar
categorias_detectadas = {}
for col in df.select_dtypes(include='object').columns:
    valores_unicos = df[col].nunique()
    if valores_unicos < 20:
        categorias_detectadas[col] = df[col].unique().tolist()

if categorias_detectadas:
    st.markdown("### 🔎 Categorías encontradas:")
    for col, valores in categorias_detectadas.items():
        st.write(f"**{col}** → {valores}")
else:
    st.info("No se encontraron columnas categóricas relevantes (menos de 20 valores únicos).")
