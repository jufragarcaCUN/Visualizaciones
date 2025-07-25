# ===================================================
# PASO 1: Importación de librerías necesarias
# ===================================================
import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import datetime
import base64  # necesario para codificar imágenes


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
archivo_principal = carpeta_base / "data" / "final_servicio_cltiene.xlsx"

# Validar si es un archivo temporal de Excel (~$)
if archivo_principal.name.startswith("~$"):
    st.error("❌ El archivo detectado es un archivo temporal de Excel (~$...). Cierra Excel y asegúrate de que el archivo real esté disponible.")
    st.stop()

# Validar existencia del archivo
if not archivo_principal.exists():
    st.error(f"❌ Error: No se encontró el archivo en la ruta: {archivo_principal}")
    st.warning("📂 Asegúrate de que 'final_servicio_cltiene.xlsx' esté dentro de la carpeta 'data' en la raíz del proyecto.")
    st.stop()

# Intentar cargar el archivo Excel
try:
    df = pd.read_excel(archivo_principal)
    #st.success(f"✅ Archivo '{archivo_principal.name}' cargado correctamente.")
except Exception as e:
    st.error(f"❌ Error al cargar el archivo Excel: {e}")
    st.stop()



# --- LÍNEA CLAVE PARA DEPURACIÓN ---
# Imprime las columnas del DataFrame para verificar si son las esperadas.
# Esta salida aparecerá en la consola o en los logs de Streamlit Cloud.
print("Columnas en el DataFrame después de la carga:", df.columns.tolist())
# -----------------------------------

# Convertir la columna 'Fecha' a formato de fecha y hora, manejando errores.
if 'Fecha' in df.columns:
    df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')
    # Aviso si hay muchas fechas nulas después de la conversión
    if df['fecha_convertida'].isnull().sum() > 0:
        st.warning("")
else:
    st.error("❌ La columna 'Fecha' no se encontró en el DataFrame. No se podrá filtrar por fecha.")

# Asegurarse de que 'Agente' sea de tipo string para evitar errores en agrupaciones/filtros.
if 'Agente' in df.columns:
    df['Agente'] = df['Agente'].astype(str)
else:
    st.error("❌ La columna 'Agente' no se encontró en el DataFrame. Esto afectará los gráficos por Agente.")

# --- INICIO DE CAMBIOS PARA SOLUCIONAR TypeError y manejo de porcentajes ---
# Convertir columnas de métricas a numérico, forzando los errores a NaN
# Esto es crucial para que las operaciones de promedio funcionen correctamente.
# Nombres de columna actualizados: 'Polarity', 'Subjectivity', 'Confianza', etc.
numeric_cols_to_convert = ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity', 'Palabras', 'Oraciones']
for col in numeric_cols_to_convert:
    if col in df.columns:
        # Si es la columna de puntaje y contiene el símbolo %, lo eliminamos primero.
        if col == 'Puntaje_Total_%' and df[col].dtype == 'object': # Comprobar si es un objeto (string)
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            # No dividimos por 100 aquí, se mantiene el valor para mostrarlo directamente como porcentaje
            # si el Excel ya lo entrega como 80.00 en lugar de 0.80.
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Verificar si quedan NaNs después de la conversión
        if df[col].isnull().sum() > 0:
            st.warning(f"⚠️ Se encontraron {df[col].isnull().sum()} valores no numéricos en la columna '{col}' después de la conversión. Estos se tratarán como nulos y no afectarán los promedios.")
    else:
        st.warning(f"⚠️ La columna '{col}' esperada para conversión numérica no se encontró en los datos. Esto podría afectar el cálculo de métricas.")
# --- FIN DE CAMBIOS PARA SOLUCIONAR TypeError ---


# ===================================================
# PASO 4: Función para mostrar métricas resumen
# ===================================================
def display_summary_metrics(df_to_display):
    st.markdown("## 📋 Resumen General de Métricas")

    # Define las métricas exactas que quieres mostrar y sus nombres de columna correspondientes
    # Nombres de columna: 'Polarity', 'Subjectivity', 'Confianza'
    metrics_to_display_map = {
        "Puntaje promedio": "Puntaje_Total_%",
        "Confianza promedio": "Confianza",
        "Polaridad promedio": "Polarity",
        "Subjetividad promedio": "Subjectivity",
    }

    # Verifica si el DataFrame contiene todas las columnas necesarias y si son numéricas
    for display_name, col_name in metrics_to_display_map.items():
        if col_name is None: # Si ya se marcó como no disponible arriba
            continue
        if col_name not in df_to_display.columns:
            st.warning(f"⚠️ La columna '{col_name}' necesaria para '{display_name}' no se encontró en los datos. Por favor, verifica el nombre de la columna.")
            metrics_to_display_map[display_name] = None # Marcar como no disponible
            continue
        if df_to_display[col_name].isnull().all():
            st.warning(f"⚠️ La columna '{col_name}' para '{display_name}' contiene solo valores nulos. No se puede calcular el promedio.")
            metrics_to_display_map[display_name] = None # Marcar como no disponible
            continue
        if not pd.api.types.is_numeric_dtype(df_to_display[col_name]):
            st.error(f"❌ La columna '{col_name}' no es numérica. Por favor, verifica el preprocesamiento de datos. Esto afectará el cálculo de métricas.")
            metrics_to_display_map[display_name] = None # Marcar como no disponible


    # Crea las columnas en Streamlit para mostrar las métricas
    cols = st.columns(5) # 4 métricas + 1 conteo de llamadas

    # Muestra el Puntaje promedio
    with cols[0]:
        if metrics_to_display_map["Puntaje promedio"]:
            promedio_puntaje = df_to_display[metrics_to_display_map["Puntaje promedio"]].mean()
            st.metric("Puntaje promedio", f"{promedio_puntaje:.2f}%")
        else:
            st.metric("Puntaje promedio", "N/A")

    # Muestra la Confianza promedio
    with cols[1]:
        if metrics_to_display_map["Confianza promedio"]:
            promedio_confianza = df_to_display[metrics_to_display_map["Confianza promedio"]].mean()
            st.metric("Confianza promedio", f"{promedio_confianza:.2f}%")
        else:
            st.metric("Confianza promedio", "N/A")

    # Muestra la Polaridad promedio (como porcentaje si quieres escalarla, si no, déjala tal cual)
    with cols[2]:
        if metrics_to_display_map["Polaridad promedio"]:
            promedio_polaridad = df_to_display[metrics_to_display_map["Polaridad promedio"]].mean()
            # La polaridad va de -1 a 1. Mostrarla como % podría ser confuso si no se escala.
            # Se muestra como decimal por defecto, puedes ajustar el formato si lo prefieres como % de 0 a 100.
            st.metric("Polaridad promedio", f"{promedio_polaridad:.2f}")
        else:
            st.metric("Polaridad promedio", "N/A")

    # Muestra la Subjetividad promedio (como porcentaje si quieres escalarla, si no, déjala tal cual)
    with cols[3]:
        if metrics_to_display_map["Subjetividad promedio"]:
            promedio_subjetividad = df_to_display[metrics_to_display_map["Subjetividad promedio"]].mean()
            # La subjetividad va de 0 a 1. Se muestra como decimal.
            st.metric("Subjetividad promedio", f"{promedio_subjetividad:.2f}")
        else:
            st.metric("Subjetividad promedio", "N/A")

    # Muestra el Conteo de llamadas
    with cols[4]:
        conteo_llamadas = len(df_to_display) # El número de filas es el conteo de llamadas
        st.metric("Conteo llamadas", f"{conteo_llamadas}")

# ===================================================
# PASO 5: Función para gráfico de puntaje total por Agente
# ===================================================
import streamlit as st
import pandas as pd
import plotly.express as px

def graficar_puntaje_total(df_to_graph):
    st.markdown("### 🎯 Promedio Total por Agente", unsafe_allow_html=True)

    # Validación de columnas requeridas
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Puntaje_Total_%' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de puntaje total. Asegúrate de tener las columnas 'Agente' y 'Puntaje_Total_%'.")
        return

    if df_to_graph['Puntaje_Total_%'].isnull().all() or not pd.api.types.is_numeric_dtype(df_to_graph['Puntaje_Total_%']):
        st.warning("⚠️ La columna 'Puntaje_Total_%' contiene solo valores nulos o no es numérica después de aplicar los filtros.")
        return

    # Agrupación por agente
    df_agrupado_por_agente = df_to_graph.groupby('Agente')['Puntaje_Total_%'].mean().reset_index()

    if df_agrupado_por_agente.empty:
        st.warning("⚠️ No hay datos para graficar el promedio total por Agente después de agrupar. Revisa tus filtros.")
        return

    # Gráfico de barras con Plotly
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
        title_x=0.5,
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # Centrar usando columnas en Streamlit
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
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

    # 🔵 Centrado visual del gráfico
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.plotly_chart(fig, use_container_width=False)

# ===================================================
# PASO 6: Función para heatmap de métricas por Agente
# ===================================================
def graficar_asesores_metricas_heatmap(df_to_graph):
    st.markdown("### 🗺️ Heatmap: Agente vs. Métricas de Conteo (Promedio)")

    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns:
        return

    metric_cols = [
        "Conteo_saludo_inicial",
        "Conteo_identificacion_cliente",
        "Conteo_comprension_problema",
        "Conteo_ofrecimiento_solucion",
        "Conteo_manejo_inquietudes",
        "Conteo_cierre_servicio",
        "Conteo_proximo_paso"
    ]

    existing_metric_cols = []
    for col in metric_cols:
        if col in df_to_graph.columns:
            if df_to_graph[col].isnull().all():
                continue
            if not pd.api.types.is_numeric_dtype(df_to_graph[col]):
                continue
            existing_metric_cols.append(col)

    if not existing_metric_cols:
        return

    df_grouped = df_to_graph.groupby('Agente')[existing_metric_cols].mean().reset_index()

    if df_grouped.empty:
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

    # 🔵 Centrado visual del gráfico
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
# ===================================================
# PASO 7: Función para indicadores tipo gauge
# ===================================================
def graficar_polaridad_subjetividad_gauges(df_to_graph):
    # Verificar si hay datos antes de intentar calcular promedios
    if df_to_graph is None or df_to_graph.empty:
        st.info("No hay datos para mostrar los indicadores de polaridad y subjetividad con los filtros actuales.")
        return

    # Creamos las columnas para organizar los gauges uno al lado del otro
    col1, col2 = st.columns(2)

    # --- Gauge de Polaridad ---
    with col1:
        st.subheader("🔍 Polaridad Promedio General")
        # Nombres de columna: 'Polarity'
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

    # --- Gauge de Subjetividad ---
    with col2:
        st.subheader("🔍 Subjectividad Promedio General")
        # Nombres de columna: 'Subjectivity'
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
    st.markdown("### 📈 Polaridad Promedio vs. Confianza Promedio por Agente")
    # Verificar si las columnas necesarias existen en el DataFrame (nombres actualizados)
    # Nombres de columna: 'Polarity', 'Subjectivity', 'Confianza'
    if df_to_graph is None or df_to_graph.empty or \
       'Agente' not in df_to_graph.columns or \
       'Polarity' not in df_to_graph.columns or \
       'Confianza' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de burbujas. Asegúrate de tener las columnas 'Agente', 'Polarity' y 'Confianza'.")
        return
    # Asegurarse de que las columnas no estén vacías después de los filtros y sean numéricas
    # Nombres de columna: 'Polarity', 'Subjectivity', 'Confianza'
    if df_to_graph['Polarity'].isnull().all() or df_to_graph['Confianza'].isnull().all() or \
       not pd.api.types.is_numeric_dtype(df_to_graph['Polarity']) or \
       not pd.api.types.is_numeric_dtype(df_to_graph['Confianza']):
        st.warning("⚠️ Las columnas 'Polarity' o 'Confianza' contienen solo valores nulos o no son numéricas después de aplicar los filtros. No se puede graficar el promedio.")
        return


    # 1. Agrupar por 'Agente' y calcular promedios de polaridad y confianza
    # 2. Contar el número de registros/llamadas por Agente
    # Nombres de columna: 'Polarity'
    df_agrupado_por_agente = df_to_graph.groupby('Agente').agg(
        promedio_polaridad=('Polarity', 'mean'),
        promedio_confianza=('Confianza', 'mean'),
        numero_llamadas=('Agente', 'count') # Cuenta el número de filas por Agente
    ).reset_index()

    if df_agrupado_por_agente.empty:
        st.warning("⚠️ No hay datos para graficar la Polaridad Promedio vs. Confianza Promedio por Agente después de agrupar. Revisa tus filtros.")
        return

    # Crear el gráfico de burbujas
    fig = px.scatter(
        df_agrupado_por_agente,
        x="promedio_polaridad",
        y="promedio_confianza",
        size="numero_llamadas", # El tamaño de la burbuja representa el número de llamadas
        # Ya no usamos 'color="Agente"' aquí para un solo color uniforme
        # Eliminamos 'color_continuous_scale' también, ya que no estamos usando una escala continua
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

    # >>> ¡CORRECCIÓN CLAVE AQUÍ! <<<
    # Establecer el color de las burbujas a un verde sólido y uniforme para TODAS.
    fig.update_traces(marker=dict(color='green', line=dict(width=1, color='DarkSlateGrey')))
    # Puedes usar un código hexadecimal específico si quieres un tono exacto de verde, por ejemplo:
    # fig.update_traces(marker=dict(color='#31a354', line=dict(width=1, color='DarkSlateGrey')))


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
# PASO 9: Función para mostrar acordeones por Agente
# ===================================================
def mostrar_acordeones(df_to_display):
    st.markdown("### 🔍 Detalle Completo por Agente") # Título ajustado a 'Agente'
    if df_to_display is None or df_to_display.empty:
        st.warning("⚠️ El DataFrame está vacío o no fue cargado correctamente.")
        return
    # COLUMNA: 'Agente'
    if 'Agente' not in df_to_display.columns:
        st.error("❌ El DataFrame no contiene la columna 'Agente'.")
        return

    # Asegurar que la columna 'Agente' sea de tipo string.
    df_to_display['Agente'] = df_to_display['Agente'].astype(str)
    unique_agentes = df_to_display['Agente'].dropna().unique()

    if unique_agentes.size == 0:
        st.info("No hay agentes disponibles para mostrar en los acordeones con los filtros actuales.")
        return

    # Columnas a excluir, ajustadas a los nombres exactos de tu DataFrame
    cols_to_exclude_from_accordion = [
        "Identificador único",
        "Telefono",
        "Puntaje_Total_%",
        "Polarity",
        "Subjectivity",
        "Confianza",
        "Palabras",
        "Oraciones",
        "asesor_corto", # Se mantiene si existe, si no, no genera error
        "fecha_convertida",
        "NombreAudios",
        "NombreAudios_Normalizado",
        "Coincidencia_Excel",
        "Archivo_Vacio",
        "Estado_Llamada",
        "Sentimiento",
        "Direccion grabacion",
        "Evento",
        "Nombre de Opción",
        "Codigo Entrante",
        "Troncal",
        "Grupo de Colas",
        "Cola", # ¡Esta columna está en tu lista!
        "Contacto",
        "Identificacion",
        "Tiempo de Espera",
        "Tiempo de Llamada",
        "Posicion de Entrada",
        "Tiempo de Timbrado",
        "Comentario",
        "audio"
    ]

    for nombre_agente in unique_agentes:
        df_agente = df_to_display[df_to_display['Agente'] == nombre_agente]

        if df_agente.empty:
            continue

        with st.expander(f"🧑 Detalle de: **{nombre_agente}** ({len(df_agente)} registros)"):
            for index, row in df_agente.iterrows():
                # COLUMNA: 'Archivo_Analizado' (asumo que esta columna existe en tu Excel final)
                archivo = row.get("Archivo_Analizado", "Archivo desconocido")
                st.write(f"📄 Analizando: **{archivo}**")

                for col in df_agente.columns: # Iterar sobre las columnas del sub-DataFrame del agente
                    # Asegurarse de que la columna no esté en la lista de exclusión o sea 'Agente'/'Archivo_Analizado'
                    if col in cols_to_exclude_from_accordion or col in ['Agente', 'Archivo_Analizado']:
                        continue

                    valor = row.get(col, 'N/A')

                    if pd.isna(valor) or valor == '' or valor is None: # Considerar también cadenas vacías o None como "sin dato"
                        st.write(f"🔹 {col.replace('_', ' ').capitalize()}: N/A ❌ (sin dato)")
                        continue

                    cumple = '❌'
                    if isinstance(valor, (int, float)):
                        # Nombres de columna: 'Puntaje_Total_%', 'Conteo_...'
                        if 'Puntaje_Total_%' in col: # La columna de puntaje total
                            cumple = '✅' if valor >= 80 else '❌'
                        # ¡CORRECCIÓN AQUÍ! Se mantiene la lógica 'Conteo_' ya que tus nuevas columnas de conteo la usan
                        elif 'Conteo_' in col:
                            cumple = '✅' if valor >= 1 else '❌'
                        else: # Para otras métricas numéricas que simplemente existen (Polarity, Subjectivity, Confianza, Palabras, Oraciones)
                            cumple = '✅'
                    # Manejo de otros tipos de datos que no son numéricos pero tienen un valor
                    else:
                        cumple = '✅' # Si tiene un valor no nulo, se asume que 'cumple'


                    st.write(f"🔹 {col.replace('_', ' ').capitalize()}: {valor} {cumple}")

                # Línea divisoria entre cada registro de llamada dentro del acordeón de un agente
                # Asegurarse de que no sea la última fila del grupo para no poner un separador al final
                if len(df_agente) > 1 and index != df_agente.index[-1]:
                    st.markdown("---")

# ===================================================
# PASO 10: Lógica principal de la aplicación (main)
# ===================================================
def main():
    st.sidebar.header("Filtros de Datos")

    # --- FILTRO POR FECHA ---
    # Asegúrate de que 'Fecha' exista y tenga datos válidos antes de intentar crear el filtro de fechas.
    if 'Fecha' in df.columns and not df['Fecha'].isnull().all():
        # Convertir a fecha directamente para el rango min/max de la UI
        temp_fecha_convertida_para_filtro = pd.to_datetime(df['Fecha'], errors='coerce').dropna()

        if not temp_fecha_convertida_para_filtro.empty:
            min_date = temp_fecha_convertida_para_filtro.min().date()
            max_date = temp_fecha_convertida_para_filtro.max().date()

            date_range = st.sidebar.date_input(
                "Selecciona rango de fechas:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            df_filtrado_fecha = df.copy() # Start with a copy
            # Asegurarse de que date_range sea una tupla de dos elementos para el filtro
            if len(date_range) == 2:
                start_date, end_date = date_range
                df_filtrado_fecha = df_filtrado_fecha[
                    (df_filtrado_fecha['fecha_convertida'].dt.date >= start_date) &
                    (df_filtrado_fecha['fecha_convertida'].dt.date <= end_date)
                ].copy() # Asegurar copia después del filtro
            elif len(date_range) == 1: # Si solo se selecciona una fecha
                start_date = date_range[0]
                df_filtrado_fecha = df_filtrado_fecha[
                    (df_filtrado_fecha['fecha_convertida'].dt.date >= start_date)
                ].copy() # Asegurar copia
            else: # Si no se selecciona nada, usar el DataFrame completo (ya es una copia)
                pass
        else:
            st.sidebar.warning("⚠️ No hay fechas válidas en los datos para mostrar el filtro de fecha.")
            df_filtrado_fecha = df.copy() # Si no hay fechas válidas, no se filtra por fecha
    else:
        st.sidebar.warning("❌ La columna 'Fecha' no existe o está vacía. No se podrá filtrar por fecha.")
        df_filtrado_fecha = df.copy() # Si no hay columna 'Fecha', se pasa el DF completo

    st.sidebar.markdown("---") # Separador visual para el filtro de agente

    # --- FILTRO POR AGENTE ---
    # Verificar si 'Agente' existe y no está completamente vacío antes de intentar obtener únicos.
    if 'Agente' in df_filtrado_fecha.columns and not df_filtrado_fecha['Agente'].dropna().empty:
        # Asegurarse de que la columna 'Agente' sea de tipo string antes de obtener únicos
        df_filtrado_fecha['Agente'] = df_filtrado_fecha['Agente'].astype(str)
        all_agents = sorted(df_filtrado_fecha['Agente'].dropna().unique().tolist())
        selected_agents = st.sidebar.multiselect(
            "👤 Selecciona Agentes:",
            options=all_agents,
            default=all_agents # Selecciona todos por defecto
        )
        # Aplicar filtro de agente
        if selected_agents:
            df_final_filtered = df_filtrado_fecha[df_filtrado_fecha['Agente'].isin(selected_agents)].copy()
        else:
            st.warning("Por favor, selecciona al menos un agente para ver los datos.")
            df_final_filtered = pd.DataFrame() # DataFrame vacío si no hay agentes seleccionados
    else:
        st.sidebar.warning("❌ La columna 'Agente' no existe o está vacía en los datos filtrados por fecha. No se podrá filtrar por Agente.")
        df_final_filtered = df_filtrado_fecha.copy() # Continúa con el DataFrame filtrado por fecha si no hay columna de agente

    st.sidebar.markdown("---") # Separador final para los filtros


    # ===================================================
    # PASO 11: Mostrar gráficos y métricas
    # ===================================================

    st.title("📊 Dashboard de Análisis de Interacciones")
    st.markdown("Bienvenido al dashboard de análisis de interacciones con clientes. Utiliza los filtros para explorar los datos.")

    if df_final_filtered.empty:
        st.warning("🚨 ¡Atención! No hay datos para mostrar con los filtros seleccionados. Ajusta tus selecciones.")
        return

    # Muestra las métricas resumen
    display_summary_metrics(df_final_filtered)
    st.markdown("---")

    st.header("📈 Gráficos Resumen")

    graficar_puntaje_total(df_final_filtered)
    st.markdown("---")

    graficar_polaridad_asesor_total(df_final_filtered)
    st.markdown("---")
    #Visualizaciones-main\Visualizaciones-main\pages\5_cl_tiene_servicio.py
    #st.write("📌 DEBUG: Entrando a heatmap con", len(df_final_filtered), "filas")
    #st.write("📌 Columnas del DataFrame en ese momento:", df_final_filtered.columns.tolist())

    graficar_asesores_metricas_heatmap(df_final_filtered)


    graficar_polaridad_subjetividad_gauges(df_final_filtered)
    st.markdown("---")

    graficar_polaridad_confianza_asesor_burbujas(df_final_filtered)
    st.markdown("---")

    # ¡La función mostrar_acordeones está de vuelta aquí, con las columnas corregidas!
    mostrar_acordeones(df_final_filtered)
    st.markdown("---") # Añadir un separador final para el acordeón

# ===================================================
# PASO 12: Punto de entrada de la app
# ===================================================
if __name__ == '__main__':
    main()
