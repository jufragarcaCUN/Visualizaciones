# ===================================================
# PASO 1: Importación de librerías necesarias
# ===================================================
import pandas as pd
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
#import locale
import datetime

# ===================================================
# PASO 2: Configuración inicial de la app
# ===================================================
st.set_page_config(layout="wide")

# ===================================================
# PASO 3: Carga y preprocesamiento del archivo principal
# ===================================================
carpeta_base = Path(__file__).parent.parent / "data"
archivo_principal = carpeta_base / "reporte_analisis_conversaciones_v2.xlsx"

try:
    df = pd.read_excel(archivo_principal)
except FileNotFoundError:
    st.error(f"Error: El archivo no se encontró en la ruta especificada: {archivo_principal}")
    st.stop()

df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')

if 'asesor' in df.columns:
    asesores = ["Todos"] + sorted(df["Agente"].dropna().unique())

# ===================================================
# PASO 4: Función para mostrar métricas resumen
# ===================================================
def display_summary_metrics(df_to_display):
    st.markdown("## 📋 Resumen General de Métricas")
    metrics_to_display_map = {
        "Puntaje promedio": "puntaje",
        "Confianza promedio": "confianza",
        "Polaridad promedio": "polarity",
        "Subjetividad promedio": "subjectivity",
    }
    for display_name, col_name in metrics_to_display_map.items():
        if col_name not in df_to_display.columns:
            st.warning(f"⚠️ La columna '{col_name}' necesaria para '{display_name}' no se encontró en los datos.")
            return

    cols = st.columns(5)
    with cols[0]:
        promedio_puntaje = df_to_display["puntaje"].mean() * 100
        st.metric("Puntaje promedio", f"{promedio_puntaje:.2f}%")
    with cols[1]:
        promedio_confianza = df_to_display["confianza"].mean() * 100
        st.metric("Confianza promedio", f"{promedio_confianza:.2f}%")
    with cols[2]:
        promedio_polaridad = df_to_display["polarity"].mean() * 100
        st.metric("Polaridad promedio", f"{promedio_polaridad:.2f}%")
    with cols[3]:
        promedio_subjetividad = df_to_display["subjectivity"].mean() * 100
        st.metric("Subjetividad promedio", f"{promedio_subjetividad:.2f}%")
    with cols[4]:
        conteo_llamadas = len(df_to_display)
        st.metric("Conteo llamadas", f"{conteo_llamadas}")

# ===================================================
# PASO 5: Función principal
# ===================================================
def main():
    st.sidebar.header("Filtros")
    asesores = ["Todos"] + sorted(df["Agente"].dropna().unique())
    asesor_seleccionado = st.sidebar.selectbox("👤 Selecciona un asesor", asesores)
    df_filtrado = df.copy()
    if asesor_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["asesor"] == asesor_seleccionado].copy()

    st.sidebar.markdown("---")
    if 'fecha_convertida' in df_filtrado.columns:
        num_fechas_no_nulas = df_filtrado['fecha_convertida'].dropna().shape[0]
        st.sidebar.write(f"📊 Total registros con fecha_convertida: {num_fechas_no_nulas}")
        if not df_filtrado['fecha_convertida'].dropna().empty:
            fechas_validas = df_filtrado['fecha_convertida'].dropna().dt.date.unique()
            fechas_ordenadas = sorted(fechas_validas)
            opciones_fechas = ["Todas"] + [str(fecha) for fecha in fechas_ordenadas]
            fecha_seleccionada = st.sidebar.selectbox("📅 Filtrar por fecha exacta", opciones_fechas)
            if fecha_seleccionada != "Todas":
                try:
                    fecha_filtrada_dt = pd.to_datetime(fecha_seleccionada).date()
                    df_filtrado = df_filtrado[df_filtrado['fecha_convertida'].dt.date == fecha_filtrada_dt]
                except Exception as e:
                    st.sidebar.error(f"❌ Error al filtrar por la fecha seleccionada: {e}")
            else:
                st.sidebar.info("Mostrando datos de todas las fechas disponibles.")
        else:
            st.sidebar.warning("⚠️ No hay fechas válidas para mostrar un selector.")
    else:
        st.sidebar.error("❌ La columna 'fecha_convertida' no existe en los datos.")

    st.sidebar.markdown("---")
    st.title("📊 Dashboard de Análisis Cartera")
    if df_filtrado.empty:
        st.warning("🚨 No hay datos para mostrar con los filtros seleccionados.")
        return

    display_summary_metrics(df_filtrado)

# ===================================================
# PASO 6: Punto de entrada
# ===================================================
if __name__ == '__main__':
    main()
