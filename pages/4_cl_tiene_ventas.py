import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import datetime

st.set_page_config(layout="wide")

# --- CARGA DE ARCHIVO ---
archivo = Path(__file__).resolve().parent.parent / "data" / "Ventas se le tiene_hoy.xlsx"
df = pd.read_excel(archivo)

# --- PREPROCESAMIENTO ---
df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
df['Agente'] = df['Agente'].astype(str)
for col in ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity']:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace('%', ''), errors='coerce')

# --- FILTROS ---
st.sidebar.title("🎛️ Filtros")

# Estado de la llamada
estado_col = "Estado de la LLamada"
if estado_col in df.columns:
    estados = ["Todos"] + sorted(df[estado_col].dropna().unique())
    estado_sel = st.sidebar.selectbox("Estado de la Llamada", estados)
    if estado_sel != "Todos":
        df = df[df[estado_col] == estado_sel]

# Fecha
min_f, max_f = df['fecha_convertida'].min(), df['fecha_convertida'].max()
fecha_ini, fecha_fin = st.sidebar.date_input("📅 Rango de Fechas", (min_f.date(), max_f.date()))
df = df[(df['fecha_convertida'] >= pd.Timestamp(fecha_ini)) & (df['fecha_convertida'] <= pd.Timestamp(fecha_fin))]

# Agentes
agentes = sorted(df['Agente'].dropna().unique())
agentes_sel = st.sidebar.multiselect("👤 Agentes", agentes, default=agentes)
df = df[df['Agente'].isin(agentes_sel)]

# --- MÉTRICAS RESUMEN ---
st.subheader("📋 Resumen General")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Puntaje promedio", f"{df['Puntaje_Total_%'].mean():.2f}%")
col2.metric("Confianza", f"{df['Confianza'].mean():.2f}%")
col3.metric("Polaridad", f"{df['Polarity'].mean():.2f}")
col4.metric("Subjetividad", f"{df['Subjectivity'].mean():.2f}")
col5.metric("Total llamadas", len(df))

# --- GRÁFICO 1: Puntaje por Agente ---
st.subheader("🎯 Puntaje Total por Agente")
fig1 = px.bar(
    df.groupby("Agente")["Puntaje_Total_%"].mean().reset_index(), 
    x="Agente",
    y="Puntaje_Total_%",
    text="Puntaje_Total_%",
    color="Puntaje_Total_%",
    color_continuous_scale="Greens"  # ⬅️ Escala verde forzada
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
    color_continuous_scale="Greens"  # ⬅️ Verde aplicado
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

# --- INDICADORES TIPO GAUGE ---
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

# --- BURBUJAS: Polaridad vs Confianza ---
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
    title="Polaridad vs Confianza",
    labels={"promedio_polaridad": "Polaridad", "promedio_confianza": "Confianza (%)"}
)
fig_bubble.update_layout(plot_bgcolor="white", height=600)
st.plotly_chart(fig_bubble, use_container_width=True)

# --- ACORDEONES POR AGENTE ---
st.subheader("🧾 Detalle por Agente")
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
        for idx, row in subset.iterrows():
            st.write(f"📄 Registro #{idx}")
            for col in subset.columns:
                if col in columnas_ocultas:
                    continue
                val = row[col]
                if pd.isna(val) or val == '':
                    st.write(f"🔹 {col}: N/A ❌")
                else:
                    st.write(f"🔹 {col}: {val}")

