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
archivo_principal = carpeta_base / "estructura_completa_final (1)"

try:
    df = pd.read_excel(archivo_principal)
    st.success(f"✅ Archivo '{archivo_principal.name}' cargado correctamente.")
except FileNotFoundError:
    st.error(f"❌ Error: El archivo no se encontró en la ruta especificada: **{archivo_principal}**")
    st.warning(f"Asegúrate de que el archivo '{archivo_principal.name}' esté en la carpeta 'data' (relativa a la ubicación de tu script del dashboard).")
    st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar el archivo Excel: {e}")
    st.stop()

print("Columnas en el DataFrame después de la carga:", df.columns.tolist())

if 'Fecha' in df.columns:
    df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
    if df['fecha_convertida'].isnull().sum() > 0:
        st.warning("Al reporte le hace falta actualizar la base de Junio y Julio")
else:
    st.error("❌ La columna 'Fecha' no se encontró en el DataFrame. No se podrá filtrar por fecha.")

if 'Agente' in df.columns:
    df['Agente'] = df['Agente'].astype(str)
else:
    st.error("❌ La columna 'Agente' no se encontró en el DataFrame. Esto afectará los gráficos por Agente.")

numeric_cols_to_convert = ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity', 'Palabras', 'Oraciones']
for col in numeric_cols_to_convert:
    if col in df.columns:
        if col == 'Puntaje_Total_%' and df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if df[col].isnull().sum() > 0:
            st.warning(f"⚠️ Se encontraron {df[col].isnull().sum()} valores no numéricos en la columna '{col}' después de la conversión.")
    else:
        st.warning(f"⚠️ La columna '{col}' esperada para conversión numérica no se encontró en los datos.")

# ===================================================
# PASO 4: Función para mostrar métricas resumen
# ===================================================
# ===================================================
# PASO 5: Gráficos fijos por Categoría y Métricas
# ===================================================
st.title("📊 Gráficas de Promedios por Categoría y Métricas Globales")

valores_categoria = {
    "Saludo": 0.0141661,
    "Presentación": 0.33548,
    "Política Grabación": 0.125885,
    "Valor Agregado": 0.098197,
    "Costos": 0.015132,
    "Pre-cierre": 0.00676111,
    "Normativos": 0.0257566
}

df_categoria = pd.DataFrame(list(valores_categoria.items()), columns=["Categoría", "Promedio"])
df_categoria["Promedio"] = df_categoria["Promedio"] * 100

fig1 = px.bar(df_categoria.sort_values("Promedio", ascending=False), x="Categoría", y="Promedio", text="Promedio", color="Promedio", color_continuous_scale="Greens", title="✅ Promedio por Categoría de Interacción (%)")
fig1.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
fig1.update_layout(height=450, xaxis_tickangle=-45, title_x=0.5, plot_bgcolor="white")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

valores_emocionales = {
    "Polaridad": 0.0373493,
    "Subjetividad": 0.0712199,
    "Confianza": 0.295827
}

df_emocional = pd.DataFrame(list(valores_emocionales.items()), columns=["Métrica", "Promedio"])
df_emocional["Promedio"] = df_emocional["Promedio"] * 100

fig2 = px.bar(df_emocional.sort_values("Promedio", ascending=False), x="Métrica", y="Promedio", text="Promedio", color="Promedio", color_continuous_scale="Blues", title="✅ Polaridad, Subjetividad y Confianza (%)")
fig2.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
fig2.update_layout(height=400, xaxis_tickangle=-25, title_x=0.5, plot_bgcolor="white")
st.plotly_chart(fig2, use_container_width=True)

# ===================================================
# PASO 12: Punto de entrada de la app
# ===================================================
if __name__ == '__main__':
    st.warning("⚠️ Función 'main()' deshabilitada temporalmente por limpieza de funciones faltantes.")
