import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import datetime
import base64 # ¡Esta importación debe estar aquí y solo aquí!

# ===================================================
# 1. Configuración inicial de la página
# ===================================================
st.set_page_config(layout="wide")

# ===================================================
# 2. Rutas y carga de datos y logos
# ===================================================
# Define la ruta base para el proyecto desde la ubicación del script actual.
# Asume que el script está en /visualizaciones/pages y 'data' está en /visualizaciones/data
project_root = Path(__file__).resolve().parent.parent
data_folder_path = project_root / "data"

# Ruta del archivo Excel
excel_file_path = data_folder_path / "Ventas se le tiene_hoy.xlsx"
df = pd.read_excel(excel_file_path)

# Ruta de la imagen COE.jpeg (¡en mayúsculas!)
logo_coe_path = data_folder_path / "COE.jpg"

# Función para codificar la imagen a Base64
def encode_image(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"❌ Error: No se encontró la imagen en: {path}. Verifica la ruta y las mayúsculas/minúsculas.")
        return ""
    except Exception as e:
        st.error(f"❌ Error al cargar la imagen {path}: {e}")
        return ""

# Cargar y codificar la imagen COE.jpeg
encoded_logo_coe = encode_image(logo_coe_path)

# ===================================================
# 3. Preprocesamiento de Datos
# ===================================================
df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
df['Agente'] = df['Agente'].astype(str)
for col in ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity']:
    df[col] = pd.to_numeric(df[col].astype(str).replace('%', ''), errors='coerce')

# ===================================================
# 4. Filtros en la barra lateral
# ===================================================
st.sidebar.title("🎛️ Filtros")

# Filtro por Estado de la Llamada
estado_col = "Estado de la LLamada" # Asegúrate que este nombre de columna sea exacto
if estado_col in df.columns:
    estados = ["Todos"] + sorted(df[estado_col].dropna().unique())
    estado_sel = st.sidebar.selectbox("Estado de la Llamada", estados)
    if estado_sel != "Todos":
        df = df[df[estado_col] == estado_sel]
else:
    st.sidebar.warning(f"La columna '{estado_col}' no se encontró en los datos.")

# Filtro por Rango de Fechas
min_f, max_f = df['fecha_convertida'].min(), df['fecha_convertida'].max()
fecha_ini, fecha_fin = st.sidebar.date_input(
    "📅 Rango de Fechas",
    (min_f.date(), max_f.date() if pd.notna(max_f) else datetime.date.today())
)
df = df[(df['fecha_convertida'] >= pd.Timestamp(fecha_ini)) &
        (df['fecha_convertida'] <= pd.Timestamp(fecha_fin))]

# Filtro por Agentes
agentes = sorted(df['Agente'].dropna().unique())
agentes_sel = st.sidebar.multiselect("👤 Agentes", agentes, default=agentes)
df = df[df['Agente'].isin(agentes_sel)]

# ===================================================
# 5. Métricas Resumen
# ===================================================
st.subheader("📋 Resumen General")
col1, col2, col3, col4, col5, col6 = st.columns(6) # Definición correcta de 6 columnas

col1.metric("Puntaje promedio", f"{df['Puntaje_Total_%'].mean():.2f}%")
col2.metric("Confianza", f"{df['Confianza'].mean():.2f}%")
col3.metric("Polaridad", f"{df['Polarity'].mean():.2f}")
col4.metric("Subjetividad", f"{df['Subjectivity'].mean():.2f}")
col5.metric("Total llamadas", len(df))

# La métrica adicional en la sexta columna con el logo y el mensaje
if encoded_logo_coe:
    with col6:
        st.markdown(
            f"""
            <div style='
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);'
            >
                <img src='data:image/jpeg;base64,{encoded_logo_coe}'
                     style='width: 60px; height: 60px; object-fit: contain; margin-bottom: 10px;' />
            
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    with col6: # Si el logo no carga, al menos mostrar un warning o un placeholder
        st.warning("⚠️ Imagen 'COE.jpeg' no cargada para la métrica adicional.")


# ===================================================
# 6. Gráficos
# ===================================================

# --- GRÁFICO 1: Puntaje por Agente ---
st.subheader("🎯 Puntaje Total por Agente")
fig1 = px.bar(
    df.groupby("Agente")["Puntaje_Total_%"].mean().reset_index(),
    x="Agente",
    y="Puntaje_Total_%",
    text="Puntaje_Total_%",
    color="Puntaje_Total_%",
    color_continuous_scale="Greens"
)
fig1.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)


# --- GRÁFICO 2: Polaridad por Agente ---
st.subheader("📊 Polaridad por Agente")
fig2 = px.bar(
    df.groupby("Agente")["Polarity"].mean().reset_index(),
    x="Agente",
    y="Polarity",
    text="Polarity",
    color="Polarity",
    color_continuous_scale="Greens"
)
fig2.update_traces(texttemplate='%{y:.2f}', textposition='outside')
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)


# --- HEATMAP ---
st.subheader("🗺️ Heatmap de Métricas")
metricas = ['apertura', 'presentacion_beneficio', 'creacion_necesidad',
            'manejo_objeciones', 'cierre', 'confirmacion_bienvenida', 'consejos_cierre']
metricas_existentes = [m for m in metricas if m in df.columns]
if metricas_existentes:
    df_heatmap = df.groupby("Agente")[metricas_existentes].mean().round(2)
    fig3 = px.imshow(df_heatmap, color_continuous_scale="Greens")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No hay columnas de métricas para el heatmap.")

# ===================================================
# 7. Indicadores Tipo Gauge
# ===================================================
colg1, colg2 = st.columns(2)

with colg1:
    st.subheader("🔍 Polaridad Promedio General")
    polaridad = df['Polarity'].mean()
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=polaridad,
        delta={'reference': 0},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': 'green'},
            'steps': [
                {'range': [-1, -0.3], 'color': '#c7e9c0'},
                {'range': [-0.3, 0.3], 'color': '#a1d99b'},
                {'range': [0.3, 1], 'color': '#31a354'}
            ],
            'threshold': {'line': {'color': "black", 'width': 2}, 'value': polaridad}
        },
        title={'text': "Polaridad Promedio"}
    ))
    st.plotly_chart(fig_g1, use_container_width=False)

with colg2:
    st.subheader("🔍 Subjetividad Promedio General")
    subjetividad = df['Subjectivity'].mean()
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=subjetividad,
        delta={'reference': 0.5},
        gauge={
            'axis': {'range': [0, 1]},
            'bar': {'color': 'green'},
            'steps': [
                {'range': [0.0, 0.3], 'color': '#e5f5e0'},
                {'range': [0.3, 0.7], 'color': '#a1d99b'},
                {'range': [0.7, 1.0], 'color': '#31a354'}
            ],
            'threshold': {'line': {'color': "black", 'width': 2}, 'value': subjetividad}
        },
        title={'text': "Subjectividad Promedio"}
    ))
    st.plotly_chart(fig_g2, use_container_width=False)

# ===================================================
# 8. Gráfico de Burbujas: Polaridad vs Confianza
# ===================================================
st.subheader("📈 Polaridad vs Confianza por Agente")
df_bubble = df.groupby("Agente").agg(
    promedio_polaridad=('Polarity', 'mean'),
    promedio_confianza=('Confianza', 'mean'),
    llamadas=('Agente', 'count')
).reset_index()

fig_bubble = px.scatter(
    df_bubble,
    x="promedio_polaridad",
    y="promedio_confianza",
    size="llamadas",
    hover_name="Agente",
    color="promedio_polaridad",
    color_continuous_scale="Greens",
    title="Polaridad vs Confianza",
    labels={
        "promedio_polaridad": "Polaridad",
        "promedio_confianza": "Confianza (%)"
    }
)

fig_bubble.update_layout(
    plot_bgcolor="white",
    height=600,
    xaxis=dict(title="Polaridad", range=[-0.1, 0.1]),
    yaxis=dict(title="Confianza (%)", range=[-1, 1])
)

st.plotly_chart(fig_bubble, use_container_width=True)

# ===================================================
# 9. Acordeones por Agente (Detalle de Registros)
# ===================================================
st.subheader("🧾 Detalle por Agente")
# Lista de columnas a ocultar en el detalle del acordeón
columnas_ocultas = [
    "Identificador único", "Telefono", "Puntaje_Total_%", "Polarity", "Subjectivity",
    "Confianza", "Palabra", "Oraciones", "asesor_corto", "fecha_convertida",
    "NombreAudios", "NombreAudios_Normalizado", "Coincidencia_Excel",
    "Archivo_Vacio", estado_col, "Sentimiento", "Direccion grabacion",
    "Evento", "Nombre de Opción", "Codigo Entrante", "Troncal",
    "Grupo de Colas", "Cola", "Contacto", "Identificacion",
    "Tiempo de Espera", "Tiempo de Llamada", "Posicion de Entrada",
    "Tiempo de Timbrado", "Comentario", "audio"
]

for agente in df['Agente'].unique():
    subset = df[df['Agente'] == agente]
    with st.expander(f"🧑 Detalle de: {agente} ({len(subset)} registros)"):
        if not subset.empty:
            for idx, row in subset.iterrows():
                st.write(f"--- Registro #{idx} ---")
                for col in subset.columns:
                    if col in columnas_ocultas:
                        continue
                    val = row[col]
                    if pd.isna(val) or str(val).strip() == '':
                        st.write(f"🔹 **{col}**: N/A ❌")
                    else:
                        st.write(f"🔹 **{col}**: {val}")
        else:
            st.info(f"No hay registros disponibles para el agente {agente} con los filtros actuales.")
