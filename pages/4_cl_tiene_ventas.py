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

# Utiliza st.cache_data para cachear la carga y preprocesamiento de datos
# Esto mejora el rendimiento de la aplicación al evitar recargar y procesar los datos
# cada vez que Streamlit re-ejecuta el script.
@st.cache_data
def load_and_preprocess_data():
    # Definir la ruta base donde se encuentra el archivo de datos.
    # __file__ es el archivo actual, .parent es la carpeta que lo contiene.
    # Asumo que 'data' está un nivel arriba de la carpeta donde se ejecuta este script.
    # Si tu estructura es diferente, ajusta esta línea.
    # Ejemplo: si el Excel está en la misma carpeta que el script, sería: carpeta_base = Path(__file__).parent
    carpeta_base = Path(__file__).parent.parent / "data"

    # Construir la ruta completa al archivo Excel principal.
    # Asegúrate de que el nombre del archivo sea el correcto que genera tu script de análisis.
    archivo_principal = carpeta_base / "e.xlsx"

    # Cargar el archivo Excel en un DataFrame de pandas.
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

    # --- LÍNEA CLAVE PARA DEPURACIÓN ---
    print("Columnas en el DataFrame después de la carga:", df.columns.tolist())
    # -----------------------------------

    # Convertir la columna 'Fecha' a formato de fecha y hora, manejando errores.
    if 'Fecha' in df.columns:
        df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
        # Aviso si hay muchas fechas nulas después de la conversión
        if df['fecha_convertida'].isnull().sum() > 0:
            st.warning(f"⚠️ Se encontraron {df['fecha_convertida'].isnull().sum()} valores nulos en la columna 'fecha_convertida' después de la conversión. Esto podría indicar un formato de fecha inconsistente en la columna 'Fecha' original.")
    else:
        st.error("❌ La columna 'Fecha' no se encontró en el DataFrame. No se podrá filtrar por fecha.")

    # Asegurarse de que 'Agente' sea de tipo string para evitar errores en agrupaciones/filtros.
    if 'Agente' in df.columns:
        df['Agente'] = df['Agente'].astype(str)
    else:
        st.error("❌ La columna 'Agente' no se encontró en el DataFrame. Esto afectará los gráficos por Agente.")

    # Convertir columnas de métricas a numérico, forzando los errores a NaN
    numeric_cols_to_convert = ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity', 'Palabras', 'Oraciones']
    for col in numeric_cols_to_convert:
        if col in df.columns:
            if col == 'Puntaje_Total_%' and df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isnull().sum() > 0:
                st.warning(f"⚠️ Se encontraron {df[col].isnull().sum()} valores no numéricos en la columna '{col}' después de la conversión. Estos se tratarán como nulos y no afectarán los promedios.")
        else:
            st.warning(f"⚠️ La columna '{col}' esperada para conversión numérica no se encontró en los datos. Esto podría afectar el cálculo de métricas.")
    return df

# ===================================================
# PASO 4: Función para mostrar métricas resumen
# ===================================================
def display_summary_metrics(df_to_display):
    st.markdown("## 📋 Resumen General de Métricas")

    metrics_to_display_map = {
        "Puntaje promedio": "Puntaje_Total_%",
        "Confianza promedio": "Confianza",
        "Polaridad promedio": "Polarity",
        "Subjetividad promedio": "Subjectivity",
    }

    # Verify if the DataFrame contains all necessary columns and if they are numeric
    for display_name, col_name in metrics_to_display_map.items():
        if col_name is None:
            continue
        if col_name not in df_to_display.columns:
            st.warning(f"⚠️ La columna '{col_name}' necesaria para '{display_name}' no se encontró en los datos. Por favor, verifica el nombre de la columna.")
            metrics_to_display_map[display_name] = None
            continue
        if df_to_display[col_name].isnull().all():
            st.warning(f"⚠️ La columna '{col_name}' para '{display_name}' contiene solo valores nulos. No se puede calcular el promedio.")
            metrics_to_display_map[display_name] = None
            continue
        if not pd.api.types.is_numeric_dtype(df_to_display[col_name]):
            st.error(f"❌ La columna '{col_name}' no es numérica. Por favor, verifica el preprocesamiento de datos. Esto afectará el cálculo de métricas.")
            metrics_to_display_map[display_name] = None


    cols = st.columns(5)

    with cols[0]:
        if metrics_to_display_map["Puntaje promedio"]:
            promedio_puntaje = df_to_display[metrics_to_display_map["Puntaje promedio"]].mean()
            st.metric("Puntaje promedio", f"{promedio_puntaje:.2f}%")
        else:
            st.metric("Puntaje promedio", "N/A")

    with cols[1]:
        if metrics_to_display_map["Confianza promedio"]:
            promedio_confianza = df_to_display[metrics_to_display_map["Confianza promedio"]].mean()
            st.metric("Confianza promedio", f"{promedio_confianza:.2f}%")
        else:
            st.metric("Confianza promedio", "N/A")

    with cols[2]:
        if metrics_to_display_map["Polaridad promedio"]:
            promedio_polaridad = df_to_display[metrics_to_display_map["Polaridad promedio"]].mean()
            st.metric("Polaridad promedio", f"{promedio_polaridad:.2f}")
        else:
            st.metric("Polaridad promedio", "N/A")

    with cols[3]:
        if metrics_to_display_map["Subjetividad promedio"]:
            promedio_subjetividad = df_to_display[metrics_to_display_map["Subjetividad promedio"]].mean()
            st.metric("Subjetividad promedio", f"{promedio_subjetividad:.2f}")
        else:
            st.metric("Subjetividad promedio", "N/A")

    with cols[4]:
        conteo_llamadas = len(df_to_display)
        st.metric("Conteo llamadas", f"{conteo_llamadas}")

# ===================================================
# PASO 5: Función para gráfico de puntaje total por Agente
# ===================================================
def graficar_puntaje_total(df_to_graph):
    st.markdown("### 🟢 Promedio por Categoría de Interacción")

    columnas = [
        "saludo_presentacion",
        "presentacion_compania",
        "politica_grabacion",
        "valor_agregado",
        "costos",
        "pre_cierre",
        "normativos"
    ]

    nombres_amigables = {
        "saludo_presentacion": "Saludo",
        "presentacion_compania": "Presentación",
        "politica_grabacion": "Política de Grabación",
        "valor_agregado": "Valor Agregado",
        "costos": "Costos",
        "pre_cierre": "Pre-cierre",
        "normativos": "Normativos"
    }

    promedios = {}
    for col in columnas:
        # Check if column exists and is numeric in the current filtered DataFrame
        if col in df_to_graph.columns and pd.api.types.is_numeric_dtype(df_to_graph[col]):
            promedio = df_to_graph[col].mean()
            if not pd.isna(promedio):
                promedios[nombres_amigables[col]] = promedio * 100

    if not promedios:
        st.info("No hay datos disponibles para graficar el promedio por categoría con los filtros actuales.")
        return

    df_resultado = pd.DataFrame(list(promedios.items()), columns=["Categoría", "Promedio"])

    fig = px.bar(
        df_resultado.sort_values("Promedio", ascending=False),
        x="Categoría",
        y="Promedio",
        text="Promedio",
        color="Promedio",
        color_continuous_scale="Greens",
        title="Promedio por Categoría (%)"
    )
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, height=500, title_x=0.5, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

# ===================================================
# Función para gráfico de polaridad por Agente
# ===================================================
def graficar_polaridad_asesor_total(df_to_graph):
    st.markdown("### 📊 Polaridad Promedio por Agente")
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Polarity' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de polaridad por Agente. Asegúrate de tener las columnas 'Agente' y 'Polarity'.")
        return
    if df_to_graph['Polarity'].isnull().all() or not pd.api.types.is_numeric_dtype(df_to_graph['Polarity']):
        st.warning("⚠️ La columna 'Polarity' contiene solo valores nulos o no es numérica después de aplicar los filtros. No se puede graficar el promedio.")
        return

    df_agrupado_por_agente = df_to_graph.groupby('Agente')['Polarity'].mean().reset_index()

    if df_agrupado_por_agente.empty:
        st.warning("⚠️ No hay datos para graficar el promedio de polaridad por Agente después de agrupar. Revisa tus filtros.")
        return

    fig = px.bar(
        df_agrupado_por_agente.sort_values("Polarity", ascending=False),
        x="Agente",
        y="Polarity",
        text="Polarity",
        color="Polarity",
        color_continuous_scale="Greens",
        title="Polaridad Promedio por Agente",
        labels={"Polarity": "Promedio de Polaridad", "Agente": "Agente"}
    )

    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(
        height=600,
        width=max(800, 50 * len(df_agrupado_por_agente)),
        xaxis_tickangle=-45,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5,
        margin=dict(b=150)
    )

    st.plotly_chart(fig, use_container_width=False)


# ===================================================
# PASO 6: Función para heatmap de métricas por Agente (Ajustada para ser una barra simple como el original parecía buscar)
# ===================================================
def graficar_asesores_metricas_heatmap(df_to_graph):
    st.markdown("### 💬 Polaridad, Subjetividad y Confianza")

    columnas = {
        "Polaridad": "Polarity",
        "Subjetividad": "Subjectivity",
        "Confianza": "Confianza"
    }

    promedios = {}
    for nombre_legible, col in columnas.items():
        if col in df_to_graph.columns and pd.api.types.is_numeric_dtype(df_to_graph[col]):
            promedio = df_to_graph[col].mean()
            if not pd.isna(promedio):
                if nombre_legible == "Confianza":
                    promedios[nombre_legible] = promedio * 100
                else:
                    promedios[nombre_legible] = promedio
        else:
            st.warning(f"⚠️ La columna '{col}' no se encontró o no es numérica en los datos filtrados para la gráfica '{nombre_legible}'.")


    if not promedios:
        st.info("No hay datos para graficar Polaridad, Subjetividad y Confianza con los filtros actuales.")
        return

    df_resultado = pd.DataFrame(list(promedios.items()), columns=["Métrica", "Promedio"])

    fig = px.bar(
        df_resultado.sort_values("Promedio", ascending=False),
        x="Métrica",
        y="Promedio",
        text="Promedio",
        color="Promedio",
        color_continuous_scale="Blues",
        title="Promedios de Polaridad, Subjetividad y Confianza"
    )

    def format_text(row):
        if row["Métrica"] == "Confianza":
            return f'{row["Promedio"]:.1f}%'
        else:
            return f'{row["Promedio"]:.2f}'

    fig.update_traces(texttemplate=[format_text(row) for _, row in df_resultado.iterrows()], textposition='outside')

    fig.update_layout(xaxis_tickangle=-45, height=400, title_x=0.5, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)


# ===================================================
# PASO 7: Función para indicadores tipo gauge
# ===================================================
def graficar_polaridad_subjetividad_gauges(df_to_graph):
    if df_to_graph is None or df_to_graph.empty:
        st.info("No hay datos para mostrar los indicadores de polaridad y subjetividad con los filtros actuales.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Polaridad Promedio General")
        if 'Polarity' in df_to_graph.columns and not df_to_graph['Polarity'].isnull().all() and pd.api.types.is_numeric_dtype(df_to_graph['Polarity']):
            polaridad_total = df_to_graph['Polarity'].mean()

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=polaridad_total,
                delta={'reference': 0},
                gauge={
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': 'green'},
                    'steps': [
                        {'range': [-1, -0.3], 'color': '#c7e9c0'},
                        {'range': [-0.3, 0.3], 'color': '#a1d99b'},
                        {'range': [0.3, 1], 'color': '#31a354'}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 2},
                        'thickness': 0.75,
                        'value': polaridad_total
                    }
                },
                title={'text': "Polaridad Promedio General"}
            ))
            fig_gauge.update_layout(
                font=dict(family="Arial", size=16),
                width=400,
                height=300
            )
            st.plotly_chart(fig_gauge, use_container_width=False)
        else:
            st.info("No hay datos de 'Polarity' para mostrar el indicador de Polaridad o la columna no es numérica.")

    with col2:
        st.subheader("🔍 Subjectividad Promedio General")
        if 'Subjectivity' in df_to_graph.columns and not df_to_graph['Subjectivity'].isnull().all() and pd.api.types.is_numeric_dtype(df_to_graph['Subjectivity']):
            subjectividad_total = df_to_graph['Subjectivity'].mean()

            fig_gauge2 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=subjectividad_total,
                delta={'reference': 0.5},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': 'green'},
                    'steps': [
                        {'range': [0.0, 0.3], 'color': '#e5f5e0'},
                        {'range': [0.3, 0.7], 'color': '#a1d99b'},
                        {'range': [0.7, 1.0], 'color': '#31a354'}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 2},
                        'thickness': 0.75,
                        'value': subjectividad_total
                    }
                },
                title={'text': "Subjectividad Promedio General"}
            ))
            fig_gauge2.update_layout(
                font=dict(family="Arial", size=16),
                width=400,
                height=300
            )
            st.plotly_chart(fig_gauge2, use_container_width=False)
        else:
            st.info("No hay datos de 'Subjectivity' para mostrar el indicador de Subjetividad o la columna no es numérica.")

# ===================================================
# PASO 8: Función para mostrar burbujas
# ===================================================
def graficar_polaridad_confianza_asesor_burbujas(df_to_graph):
    st.markdown("### 🎈 Polaridad vs. Confianza por Agente (Gráfico de Burbujas)")
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Polarity' not in df_to_graph.columns or 'Confianza' not in df_to_graph.columns:
        st.info("Faltan columnas ('Agente', 'Polarity', 'Confianza') o no hay datos para el gráfico de burbujas.")
        return

    # Asegurarse de que las columnas sean numéricas antes de promediar
    numeric_cols = ['Polarity', 'Confianza']
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df_to_graph[col]):
            st.warning(f"La columna '{col}' no es numérica. No se puede generar el gráfico de burbujas.")
            return

    df_grouped = df_to_graph.groupby('Agente').agg(
        Polarity_Mean=('Polarity', 'mean'),
        Confianza_Mean=('Confianza', 'mean'),
        Call_Count=('Agente', 'size') # Usar el tamaño del grupo como el tamaño de la burbuja
    ).reset_index()

    if df_grouped.empty:
        st.info("No hay datos para graficar las burbujas de Polaridad y Confianza por Agente después de agrupar.")
        return

    # Escalar confianza para mostrarla como porcentaje en el tooltip si es necesario
    df_grouped['Confianza_Mean_Pct'] = df_grouped['Confianza_Mean'] * 100

    fig = px.scatter(
        df_grouped,
        x="Confianza_Mean_Pct",
        y="Polarity_Mean",
        size="Call_Count",
        color="Agente",
        hover_name="Agente",
        size_max=60,
        title="Polaridad Promedio vs. Confianza Promedio por Agente",
        labels={
            "Confianza_Mean_Pct": "Confianza Promedio (%)",
            "Polarity_Mean": "Polaridad Promedio",
            "Call_Count": "Conteo de Llamadas"
        }
    )

    fig.update_layout(
        xaxis_title="Confianza Promedio (%)",
        yaxis_title="Polaridad Promedio",
        plot_bgcolor="white",
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)


# ===================================================
# PASO 10: Función principal de la aplicación Streamlit
# ===================================================
def main():
    df = load_and_preprocess_data()

    # --- FILTROS EN EL SIDEBAR ---
    st.sidebar.header("Filtros")

    # Filtro por Agente
    if 'Agente' in df.columns:
        agentes = sorted(df['Agente'].unique())
        selected_agentes = st.sidebar.multiselect("Seleccionar Agente(s)", agentes, default=agentes)
    else:
        selected_agentes = []
        st.sidebar.warning("La columna 'Agente' no está disponible para filtrar.")

    # Filtro por Rango de Fechas
    df_filtered_by_date = df.copy() # Inicializar con el df completo
    if 'fecha_convertida' in df.columns and not df['fecha_convertida'].isnull().all():
        min_date = df['fecha_convertida'].min().date()
        max_date = df['fecha_convertida'].max().date()

        date_range = st.sidebar.date_input(
            "Seleccionar rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1, microseconds=-1) # Incluir todo el día final
            df_filtered_by_date = df[(df['fecha_convertida'] >= start_date) & (df['fecha_convertida'] <= end_date)]
        elif len(date_range) == 1:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[0]) + pd.Timedelta(days=1, microseconds=-1)
            df_filtered_by_date = df[(df['fecha_convertida'] >= start_date) & (df['fecha_convertida'] <= end_date)]
    else:
        st.sidebar.warning("La columna 'Fecha' no está disponible o no tiene fechas válidas para filtrar.")

    # Aplicar filtros
    if selected_agentes:
        df_final = df_filtered_by_date[df_filtered_by_date['Agente'].isin(selected_agentes)].copy()
    else:
        df_final = df_filtered_by_date.copy()

    if df_final.empty:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        return # Detener la ejecución si no hay datos

    # ===================================================
    # PASO 11: Ejecución de las funciones de visualización con datos filtrados
    # ===================================================

    st.title("📞 Dashboard de Análisis de Llamadas")

    display_summary_metrics(df_final)

    st.markdown("---")

    graficar_puntaje_total(df_final)

    st.markdown("---")

    graficar_polaridad_asesor_total(df_final)

    st.markdown("---")

    graficar_asesores_metricas_heatmap(df_final)

    st.markdown("---")

    graficar_polaridad_subjetividad_gauges(df_final)

    st.markdown("---")

    graficar_polaridad_confianza_asesor_burbujas(df_final)

    st.markdown("---")

    # Eliminada la llamada a mostrar_acordeones(df_final)

# ===================================================
# Ejecución de la aplicación
# ===================================================
if __name__ == "__main__":
    main()
