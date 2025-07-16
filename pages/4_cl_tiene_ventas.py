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

# Definir la ruta base del proyecto (sube desde /pages hasta la raíz del proyecto)
carpeta_base = Path(__file__).resolve().parent.parent

# Ruta completa al archivo Excel dentro de la carpeta 'data'
archivo_principal = carpeta_base / "data" / "Ventas se le tiene_hoy.xlsx"

# Validar si es un archivo temporal de Excel (~$)
if archivo_principal.name.startswith("~$"):
    st.error("❌ El archivo detectado es un archivo temporal de Excel (~$...). Cierra Excel y asegúrate de que el archivo real esté disponible.")
    st.stop()

# Validar existencia del archivo
if not archivo_principal.exists():
    st.error(f"❌ Error: No se encontró el archivo en la ruta: {archivo_principal}")
    st.warning("📂 Asegúrate de que 'Ventas se le tiene_hoy.xlsx' esté dentro de la carpeta 'data' en la raíz del proyecto.")
    st.stop()

# Intentar cargar el archivo Excel
try:
    df = pd.read_excel(archivo_principal)
    st.success(f"✅ Archivo '{archivo_principal.name}' cargado correctamente.")
    # --- VERIFICACIÓN ADICIONAL: Si el DataFrame está vacío ---
    if df.empty:
        st.error("❌ El archivo Excel se cargó, pero el DataFrame resultante está vacío. Asegúrate de que tu Excel contiene datos en la primera hoja.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar el archivo Excel: {e}")
    st.stop()

# --- SECCIÓN CRÍTICA DE DEBUGGING DE COLUMNAS ---
# ¡ESTO SE IMPRIMIRÁ EN LA CONSOLA (TERMINAL) DONDE EJECUTAS STREAMLIT RUN!
#print("\n--- NOMBRES DE COLUMNAS DETECTADOS EN CONSOLA (TERMINAL) ---")
#print(df.columns.tolist())
#print("-----------------------------------------------------------\n")

# Esto se imprimirá en la barra lateral de Streamlit (si el df no está vacío)
#st.sidebar.markdown("---")
#st.sidebar.subheader("Nombres de columnas detectados en tu Excel:")
#for col in df.columns:
    #st.sidebar.write(f"- `{col}`")
#st.sidebar.markdown("---")
# -------------------------------------------------

# Preprocesamiento inicial (fuera de cualquier filtro dinámico)
# Convertir la columna 'Fecha' a formato de fecha y hora, manejando errores.
if 'Fecha' in df.columns:
    df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
    # Aviso si hay muchas fechas nulas después de la conversión
    if df['fecha_convertida'].isnull().sum() > 0:
        st.warning("⚠️ Se encontraron fechas nulas después de la conversión en la columna 'Fecha'.")
else:
    st.error("❌ La columna 'Fecha' no se encontró en el DataFrame. No se podrá filtrar por fecha.")

# Asegurarse de que 'Agente' sea de tipo string para evitar errores en agrupaciones/filtros.
if 'Agente' in df.columns:
    df['Agente'] = df['Agente'].astype(str)
else:
    st.error("❌ La columna 'Agente' no se encontró en el DataFrame. Esto afectará los gráficos por Agente.")

# --- CORRECCIÓN: 'Palabras' a 'Palabra' según tu lista de columnas ---
numeric_cols_to_convert = ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity', 'Palabra', 'Oraciones']
for col in numeric_cols_to_convert:
    if col in df.columns:
        # Si es la columna de puntaje y contiene el símbolo %, lo eliminamos primero.
        if col == 'Puntaje_Total_%' and df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        if df[col].isnull().sum() > 0:
            st.warning(f"⚠️ Se encontraron {df[col].isnull().sum()} valores no numéricos en la columna '{col}' después de la conversión. Estos se tratarán como nulos y no afectarán los promedios.")


# ===================================================
# 4. Implementación del filtro general: Estado de la Llamada
# ===================================================
# --- ¡IMPORTANTE! ESTE NOMBRE DEBE COINCIDIR EXACTAMENTE CON TU EXCEL ---
# Según tu lista, el nombre correcto es 'Estado de la LLamada'
CALL_STATUS_COL = 'Estado de la LLamada'

st.sidebar.markdown("## 🎛️ Filtro general")
df_current_filtered = df.copy() # DataFrame base para aplicar filtros en cadena

if CALL_STATUS_COL not in df_current_filtered.columns:
    st.sidebar.error(f"❌ La columna '{CALL_STATUS_COL}' no se encontró en el DataFrame. El filtro de estado de llamada no funcionará.")
    estado_llamada_seleccionado = "Todos" # Se asume "Todos" si la columna no existe.
else:
    # Aseguramos que la columna 'Estado de la LLamada' sea string para el selectbox
    df_current_filtered[CALL_STATUS_COL] = df_current_filtered[CALL_STATUS_COL].astype(str)
    # DEBUG: Imprimir valores únicos de Estado de la LLamada
    print(f"DEBUG: Valores únicos de '{CALL_STATUS_COL}' antes del selectbox: {df_current_filtered[CALL_STATUS_COL].unique().tolist()}")

    # Obtenemos las opciones únicas de la columna, añadiendo "Todos" al principio
    opciones_estado_llamada = ["Todos"] + sorted(list(df_current_filtered[CALL_STATUS_COL].unique()))
    estado_llamada_seleccionado = st.sidebar.selectbox(
        "Filtrar por Estado de la Llamada:",
        options=opciones_estado_llamada,
        index=0 # Por defecto, selecciona "Todos"
    )

if CALL_STATUS_COL in df.columns and estado_llamada_seleccionado != "Todos":
    df_current_filtered = df_current_filtered[
        df_current_filtered[CALL_STATUS_COL] == estado_llamada_seleccionado
    ].copy() # Aseguramos una nueva copia después de filtrar
print(f"DEBUG: df_current_filtered shape after Estado de la Llamada filter: {df_current_filtered.shape}")

# El df_current_filtered se pasa implícitamente al siguiente bloque a través del estado de la aplicación.
# ===================================================
# Lógica de filtrado del DataFrame principal (Encadenamiento)
# Este bloque asume que df_current_filtered ya ha sido definido y posiblemente filtrado
# por el "Estado de la Llamada" en el bloque anterior.
# ===================================================

# Filtro de fecha
if 'fecha_convertida' in df_current_filtered.columns:
    min_date = df_current_filtered['fecha_convertida'].min().date() if not df_current_filtered['fecha_convertida'].isnull().all() else datetime.date.today() - datetime.timedelta(days=365)
    max_date = df_current_filtered['fecha_convertida'].max().date() if not df_current_filtered['fecha_convertida'].isnull().all() else datetime.date.today()

    if min_date > max_date:
        min_date = max_date - datetime.timedelta(days=7)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📅 Filtro por Fecha")
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    fecha_inicio_dt = datetime.datetime.combine(fecha_inicio, datetime.time.min)
    fecha_fin_dt = datetime.datetime.combine(fecha_fin, datetime.time.max)

    df_current_filtered = df_current_filtered[
        (df_current_filtered['fecha_convertida'] >= fecha_inicio_dt) &
        (df_current_filtered['fecha_convertida'] <= fecha_fin_dt)
    ].copy()
else:
    st.sidebar.warning("La columna 'Fecha' no está disponible para filtrar por fecha.")
print(f"DEBUG: df_current_filtered shape after Fecha filter: {df_current_filtered.shape}")


# FILTRO DE AGENTE
if 'Agente' in df_current_filtered.columns:
    df_current_filtered['Agente'] = df_current_filtered['Agente'].astype(str)
    # DEBUG: Imprimir valores únicos de Agente
    print(f"DEBUG: Valores únicos de 'Agente' antes del multiselect: {df_current_filtered['Agente'].unique().tolist()}")

    agentes_unicos = df_current_filtered['Agente'].dropna().unique()
    agentes_unicos.sort()
    agentes_seleccionados = st.sidebar.multiselect(
        "Filtrar por Agente:",
        options=agentes_unicos,
        default=agentes_unicos
    )

    if agentes_seleccionados:
        df_current_filtered = df_current_filtered[df_current_filtered['Agente'].isin(agentes_seleccionados)].copy()
    else:
        st.warning("Por favor, selecciona al menos un agente para mostrar los datos.")
        df_current_filtered = pd.DataFrame() # Si no hay agentes seleccionados, el DF final está vacío
else:
    st.error("❌ La columna 'Agente' no se encontró en el DataFrame para aplicar el filtro.")
print(f"DEBUG: df_current_filtered shape after Agente filter: {df_current_filtered.shape}")

df_final = df_current_filtered # Asignar el DataFrame final después de todos los filtros


# ===================================================
# PASO 5: Función para mostrar métricas resumen
# ===================================================
def display_summary_metrics(df_to_display):
    st.markdown("## 📋 Resumen General de Métricas")

    # --- ¡IMPORTANTE! ESTOS VALORES DEBEN COINCIDIR EXACTAMENTE CON TUS COLUMNAS EN EL EXCEL ---
    # Según tu lista de columnas: 'Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity'
    metrics_to_display_map = {
        "Puntaje promedio": "Puntaje_Total_%",
        "Confianza promedio": "Confianza",
        "Polaridad promedio": "Polarity",
        "Subjetividad promedio": "Subjectivity",
    }

    # --- DEBUGGING ADICIONAL: Imprimir el diccionario y las columnas del DF ---
    print("\n--- DEBUGGING DENTRO DE display_summary_metrics ---")
    print(f"Keys en metrics_to_display_map (inicial): {metrics_to_display_map.keys()}")
    print(f"Columnas en df_to_display (al inicio de la función): {df_to_display.columns.tolist()}")
    print("---------------------------------------------------\n")

    cols_missing = []
    # Usamos una copia para las validaciones y para almacenar los nombres de columna válidos
    validated_metrics_map = {}
    for display_name, col_name_expected in metrics_to_display_map.items():
        if col_name_expected not in df_to_display.columns:
            cols_missing.append(f"'{col_name_expected}' (para '{display_name}')")
            validated_metrics_map[display_name] = None # Marca como None si la columna no existe
            continue
        if df_to_display[col_name_expected].isnull().all():
            st.warning(f"⚠️ La columna '{col_name_expected}' para '{display_name}' contiene solo valores nulos. No se puede calcular el promedio.")
            validated_metrics_map[display_name] = None
            continue
        if not pd.api.types.is_numeric_dtype(df_to_display[col_name_expected]):
            st.error(f"❌ La columna '{col_name_expected}' no es numérica. Por favor, verifica el preprocesamiento de datos. Esto afectará el cálculo de métricas.")
            validated_metrics_map[display_name] = None
            continue
        validated_metrics_map[display_name] = col_name_expected # Si todo está bien, guarda el nombre de la columna

    if cols_missing:
        st.warning(f"⚠️ Algunas columnas necesarias no se encontraron: {', '.join(cols_missing)}. Por favor, verifica el nombre de las columnas en tu Excel.")

    # --- DEBUGGING ADICIONAL: Imprimir el mapa validado ---
    print("\n--- DEBUGGING: validated_metrics_map después de la validación ---")
    print(validated_metrics_map)
    print("---------------------------------------------------\n")

    cols = st.columns(5)

    with cols[0]:
        # Verificamos si la clave existe y si su valor no es None
        if "Puntaje promedio" in validated_metrics_map and validated_metrics_map["Puntaje promedio"]:
            promedio_puntaje = df_to_display[validated_metrics_map["Puntaje promedio"]].mean()
            st.metric("Puntaje promedio", f"{promedio_puntaje:.2f}%")
        else:
            st.metric("Puntaje promedio", "N/A")

    with cols[1]:
        if "Confianza promedio" in validated_metrics_map and validated_metrics_map["Confianza promedio"]:
            promedio_confianza = df_to_display[validated_metrics_map["Confianza promedio"]].mean()
            st.metric("Confianza promedio", f"{promedio_confianza:.2f}%")
        else:
            st.metric("Confianza promedio", "N/A")

    with cols[2]:
        # CORRECCIÓN CLAVE: Usar validated_metrics_map aquí
        if "Polaridad promedio" in validated_metrics_map and validated_metrics_map["Polaridad promedio"]:
            # --- DEBUGGING ESPECÍFICO PARA POLARIDAD ---
            print(f"DEBUG: Valor de validated_metrics_map['Polaridad promedio']: {validated_metrics_map['Polaridad promedio']}")
            #print(f"DEBUG: Columnas de df_to_display en este punto: {df_to_display.columns.tolist()}")
            # ------------------------------------------
            promedio_polaridad = df_to_display[validated_metrics_map["Polaridad promedio"]].mean()
            st.metric("Polaridad promedio", f"{promedio_polaridad:.2f}")
        else:
            st.metric("Polaridad promedio", "N/A")

    with cols[3]:
        if "Subjetividad promedio" in validated_metrics_map and validated_metrics_map["Subjetividad promedio"]:
            promedio_subjetividad = df_to_display[validated_metrics_map["Subjetividad promedio"]].mean()
            st.metric("Subjetividad promedio", f"{promedio_subjetividad:.2f}")
        else:
            st.metric("Subjetividad promedio", "N/A")

    with cols[4]:
        conteo_llamadas = len(df_to_display)
        st.metric("Conteo llamadas", f"{conteo_llamadas}")

# ===================================================
# PASO 6: Función para gráfico de puntaje total por Agente
# ===================================================
def graficar_puntaje_total(df_to_graph):
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("### 🎯 Promedio Total por Agente")
        # Asegurarse de que 'Puntaje_Total_%' existe y es numérica
        if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Puntaje_Total_%' not in df_to_graph.columns:
            st.warning("⚠️ Datos incompletos para la gráfica de puntaje total. Asegúrate de tener las columnas 'Agente' y 'Puntaje_Total_%'.")
            return
        if df_to_graph['Puntaje_Total_%'].isnull().all() or not pd.api.types.is_numeric_dtype(df_to_graph['Puntaje_Total_%']):
            st.warning("⚠️ La columna 'Puntaje_Total_%' contiene solo valores nulos o no es numérica después de aplicar los filtros. No se puede graficar el promedio.")
            return

        df_agrupado_por_agente = df_to_graph.groupby('Agente')['Puntaje_Total_%'].mean().reset_index()

        if df_agrupado_por_agente.empty:
            st.warning("⚠️ No hay datos para graficar el promedio total por Agente después de agrupar. Revisa tus filtros.")
            return

        fig = px.bar(
            df_agrupado_por_agente.sort_values("Puntaje_Total_%", ascending=False),
            x="Agente",
            y="Puntaje_Total_%",
            text="Puntaje_Total_%",
            color="Puntaje_Total_%",
            color_continuous_scale="Greens",
            title="Promedio Total por Agente",
            labels={"Puntaje_Total_%": "Promedio de Puntaje (%)", "Agente": "Agente"}
        )
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        fig.update_layout(
            height=600,
            xaxis_tickangle=-45,
            plot_bgcolor="white",
            font=dict(family="Arial", size=14),
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

# ===================================================
# Función para gráfico de polaridad por Agente
# ===================================================
def graficar_polaridad_asesor_total(df_to_graph):
    st.markdown("### 📊 Polaridad Promedio por Agente")
    # Asegurarse de que 'Polarity' existe y es numérica
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Polarity' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de polaridad por Agente. Asegúrate de tener las columnas 'Agente' y 'Polarity'.")
        return

    # Asegurarse de que 'Polarity' es numérica
    if 'Polarity' in df_to_graph.columns:
        df_to_graph.loc[:, 'Polarity'] = pd.to_numeric(df_to_graph['Polarity'], errors='coerce')

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
    chart_width = max(800, 50 * len(df_agrupado_por_agente))

    fig.update_layout(
        height=600,
        width=chart_width,
        xaxis_tickangle=-45,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5,
        margin=dict(b=150)
    )

    col_left_spacer, col_chart, col_right_spacer = st.columns([1, 5, 1])

    with col_chart:
        st.plotly_chart(fig, use_container_width=False)

# ===================================================
# PASO 7: Función para heatmap de métricas por Agente
# ===================================================
def graficar_asesores_metricas_heatmap(df_to_graph):
    st.markdown("### 🗺️ Heatmap: Agente vs. Métricas de Conteo (Promedio)")

    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para el Heatmap. Asegúrate de tener la columna 'Agente' y datos.")
        return

    metric_cols = [
        "apertura",
        "presentacion_beneficio",
        "creacion_necesidad",
        "manejo_objeciones",
        "cierre",
        "confirmacion_bienvenida",
        "consejos_cierre"
    ]

    existing_metric_cols = []
    for col in metric_cols:
        if col not in df_to_graph.columns:
            continue
        df_to_graph.loc[:, col] = pd.to_numeric(df_to_graph[col], errors='coerce')
        if df_to_graph[col].isnull().all() or not pd.api.types.is_numeric_dtype(df_to_graph[col]):
            continue
        existing_metric_cols.append(col)

    if not existing_metric_cols:
        st.warning("⚠️ ¡Alerta! No quedan columnas válidas para el Heatmap después de la validación de datos (ninguna columna métrica cumple los requisitos).")
        return

    df_grouped = df_to_graph.groupby('Agente')[existing_metric_cols].mean().reset_index()
    df_grouped[existing_metric_cols] = df_grouped[existing_metric_cols] * 100
    df_grouped[existing_metric_cols] = df_grouped[existing_metric_cols].round(2)

    if df_grouped.empty:
        st.warning("No hay datos para mostrar en el Heatmap después de agrupar por Agente (el DataFrame agrupado está vacío).")
        return

    df_heatmap = df_grouped.set_index("Agente")[existing_metric_cols]

    fig2 = px.imshow(
        df_heatmap,
        labels=dict(x="Métrica", y="Agente", color="Valor promedio"),
        color_continuous_scale='Greens',
        aspect="auto",
        title="Heatmap: Agente vs. Métricas de Conteo (Promedio)"
    )

    fig2.update_layout(
        font=dict(family="Arial", size=12),
        height=700,
        title_x=0.5,
        plot_bgcolor='white'
    )

    st.plotly_chart(fig2, use_container_width=True)

# ===================================================
# PASO 8: Función para indicadores tipo gauge
# ===================================================
def graficar_polaridad_subjetividad_gauges(df_to_graph):
    if df_to_graph is None or df_to_graph.empty:
        st.info("No hay datos para mostrar los indicadores de polaridad y subjetividad con los filtros actuales.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Polaridad Promedio General")
        # Asegurarse de que 'Polarity' existe y es numérica
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
        # Asegurarse de que 'Subjectivity' existe y es numérica
        if 'Subjectivity' in df_to_graph.columns and not df_to_graph['Subjectivity'].isnull().all() and pd.api.types.is_numeric_dtype(df_to_graph['Subjectivity']):
            subjectividad_total = df_to_graph['Subjectivity'].mean()

            # Mover la creación y visualización del gráfico dentro de este bloque if
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
# PASO 9: Función para mostrar burbujas
# ===================================================
def graficar_polaridad_confianza_asesor_burbujas(df_to_graph):
    st.markdown("### 📈 Polaridad Promedio vs. Confianza Promedio por Agente")
    # Asegurarse de que 'Polarity' y 'Confianza' existen y son numéricas
    if df_to_graph is None or df_to_graph.empty or \
       'Agente' not in df_to_graph.columns or \
       'Polarity' not in df_to_graph.columns or \
       'Confianza' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de burbujas. Asegúrate de tener las columnas 'Agente', 'Polarity' y 'Confianza'.")
        return

    if df_to_graph['Polarity'].isnull().all() or df_to_graph['Confianza'].isnull().all() or \
       not pd.api.types.is_numeric_dtype(df_to_graph['Polarity']) or \
       not pd.api.types.is_numeric_dtype(df_to_graph['Confianza']):
        st.warning("⚠️ Las columnas 'Polarity' o 'Confianza' contienen solo valores nulos o no son numéricas después de aplicar los filtros. No se puede graficar el promedio.")
        return

    df_agrupado_por_agente = df_to_graph.groupby('Agente').agg(
        promedio_polaridad=('Polarity', 'mean'),
        promedio_confianza=('Confianza', 'mean'),
        numero_llamadas=('Agente', 'count')
    ).reset_index()

    if df_agrupado_por_agente.empty:
        st.warning("⚠️ No hay datos para graficar la Polaridad Promedio vs. Confianza Promedio por Agente después de agrupar. Revisa tus filtros.")
        return

    fig = px.scatter(
        df_agrupado_por_agente,
        x="promedio_polaridad",
        y="promedio_confianza",
        size="numero_llamadas",
        hover_name="Agente",
        hover_data={
            "promedio_polaridad": ":.2f",
            "promedio_confianza": ":.2f",
            "numero_llamadas": True
        },
        title="Polaridad Promedio vs. Confianza Promedio por Agente",
        labels={
            "promedio_polaridad": "Polaridad Promedio",
            "promedio_confianza": "Confianza Promedio (%)",
            "numero_llamadas": "Número de Llamadas"
        }
    )

    fig.update_traces(marker=dict(color='green', line=dict(width=1, color='DarkSlateGrey')))

    fig.update_layout(
        xaxis_title="Polaridad Promedio",
        yaxis_title="Confianza Promedio (%)",
        height=600,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)

# ===================================================
# PASO 10: Función para mostrar acordeones por Agente
# ===================================================
def mostrar_acordeones(df_to_display):
    st.markdown("### 🔍 Detalle Completo por Agente")
    if df_to_display is None or df_to_display.empty:
        st.warning("⚠️ El DataFrame está vacío o no fue cargado correctamente.")
        return
    if 'Agente' not in df_to_display.columns:
        st.error("❌ El DataFrame no contiene la columna 'Agente'.")
        return

    df_to_display['Agente'] = df_to_display['Agente'].astype(str)
    unique_agentes = df_to_display['Agente'].dropna().unique()

    if unique_agentes.size == 0:
        st.info("No hay agentes disponibles para mostrar en los acordeones con los filtros actuales.")
        return

    cols_to_exclude_from_accordion = [
        "Identificador único", "Telefono", "Puntaje_Total_%", "Polarity", "Subjectivity",
        "Confianza", "Palabra", "Oraciones", "asesor_corto", "fecha_convertida",
        "NombreAudios", "NombreAudios_Normalizado", "Coincidencia_Excel",
        "Archivo_Vacio", CALL_STATUS_COL, "Sentimiento", "Direccion grabacion",
        "Evento", "Nombre de Opción", "Codigo Entrante", "Troncal",
        "Grupo de Colas", "Cola", "Contacto", "Identificacion",
        "Tiempo de Espera", "Tiempo de Llamada", "Posicion de Entrada",
        "Tiempo de Timbrado", "Comentario", "audio"
    ]

    for nombre_agente in unique_agentes:
        df_agente = df_to_display[df_to_display['Agente'] == nombre_agente]

        if df_agente.empty:
            continue

        with st.expander(f"🧑 Detalle de: **{nombre_agente}** ({len(df_agente)} registros)"):
            for index, row in df_agente.iterrows():
                archivo = row.get("Archivo_Analizado", "Archivo desconocido")
                st.write(f"📄 Analizando: **{archivo}**")

                for col in df_agente.columns:
                    if col in cols_to_exclude_from_accordion or col in ['Agente', 'Archivo_Analizado']:
                        continue

                    valor = row.get(col, 'N/A')

                    if pd.isna(valor) or valor == '' or valor is None:
                        st.write(f"🔹 {col.replace('_', ' ').capitalize()}: N/A ❌ (sin dato)")
                        continue

                    cumple = '❌'
                    if isinstance(valor, (int, float)):
                        if 'Puntaje_Total_%' in col:
                            cumple = '✅' if valor >= 80 else '❌'
                        elif 'Conteo_' in col:
                            cumple = '✅' if valor >= 1 else '❌'
                        else:
                            cumple = '✅'
                    else:
                        cumple = '✅'

                    st.write(f"🔹 {col.replace('_', ' ').capitalize()}: {valor} {cumple}")

# ===================================================
# Flujo principal de la aplicación (parte final)
# ===================================================

# Mensaje si el DataFrame final está vacío después de todos los filtros
if df_final.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
else:
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
    mostrar_acordeones(df_final)

