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
# Definir la ruta base donde se encuentra el archivo de datos.
carpeta_base = Path(__file__).parent.parent / "data"
# Construir la ruta completa al archivo Excel principal.
# CAMBIO AQUÍ: Nombre del archivo Excel actualizado
archivo_principal = carpeta_base / "reporte_analisis_conversaciones_v2.xlsx"

# Cargar el archivo Excel en un DataFrame de pandas.
try:
    df = pd.read_excel(archivo_principal)
except FileNotFoundError:
    st.error(f"Error: El archivo no se encontró en la ruta especificada: {archivo_principal}")
    st.stop() # Detiene la ejecución de la aplicación si el archivo no se encuentra.

# --- LÍNEA CLAVE PARA DEPURACIÓN ---
# Por favor, copia y pega la salida de esta línea aquí.
print("Columnas en el DataFrame después de la carga:", df.columns)
# -----------------------------------

# Convertir la columna 'Fecha' a formato de fecha y hora, manejando errores.
# Se asume que la columna ahora se llama 'Fecha' (con F mayúscula).
# Si esta línea sigue dando error, el nombre 'Fecha' no es el exacto.
df['fecha_convertida'] = pd.to_datetime(df['Fecha'], errors='coerce')

# Asegurarse de que 'Agente' sea de tipo string para evitar errores en agrupaciones/filtros.
# Se asume que la columna ahora se llama 'Agente'
if 'Agente' in df.columns:
    df['Agente'] = df['Agente'].astype(str)

# --- INICIO DE CAMBIOS PARA SOLUCIONAR TypeError y manejo de porcentajes ---
# Convertir columnas de métricas a numérico, forzando los errores a NaN
# Esto es crucial para que las operaciones de promedio funcionen correctamente.
numeric_cols_to_convert = ['Puntaje_Total_%', 'Confianza', 'Polarity', 'Subjectivity', 'Palabras', 'Oraciones']
for col in numeric_cols_to_convert:
    if col in df.columns:
        # Si es la columna de puntaje y contiene el símbolo %, lo eliminamos primero.
        if col == 'Puntaje_Total_%' and df[col].dtype == 'object': # Comprobar si es un objeto (string)
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            # También podríamos dividir por 100 aquí si el porcentaje se debe tratar como decimal
            # df[col] = pd.to_numeric(df[col], errors='coerce') / 100
            # Pero dado que se espera 100.00% y se usa así en display_summary_metrics,
            # lo mantenemos como el valor entero/flotante sin dividir por 100
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        st.warning(f"⚠️ La columna '{col}' esperada para conversión numérica no se encontró en los datos. Esto podría afectar el cálculo de métricas.")
# --- FIN DE CAMBIOS PARA SOLUCIONAR TypeError ---


# ===================================================
# PASO 4: Función para mostrar métricas resumen
# ===================================================
def display_summary_metrics(df_to_display):
    st.markdown("## 📋 Resumen General de Métricas")

    # Define las métricas exactas que quieres mostrar y sus nombres de columna correspondientes
    # en el DataFrame. Nombres actualizados según la lista proporcionada.
    metrics_to_display_map = {
        "Puntaje promedio": "Puntaje_Total_%",
        "Confianza promedio": "Confianza",
        "Polaridad promedio": "Polarity",
        "Subjetividad promedio": "Subjectivity",
    }

    # Verifica si el DataFrame contiene todas las columnas necesarias
    for display_name, col_name in metrics_to_display_map.items():
        # Añadir un chequeo adicional para asegurar que las columnas sean numéricas antes de calcular el promedio
        if col_name not in df_to_display.columns:
            st.warning(f"⚠️ La columna '{col_name}' necesaria para '{display_name}' no se encontró en los datos. Por favor, verifica el nombre de la columna.")
            return
        # Se asume que la conversión a numérico se hizo en el paso 3.
        # Un valor nulo en todo el subset de datos también podría causar problemas si no se maneja bien.
        if df_to_display[col_name].isnull().all():
            st.warning(f"⚠️ La columna '{col_name}' para '{display_name}' contiene solo valores nulos. No se puede calcular el promedio.")
            return


    # Crea las columnas en Streamlit para mostrar las métricas
    # Necesitamos 5 columnas: 4 para los promedios y 1 para el conteo de llamadas.
    cols = st.columns(5)

    # Muestra el Puntaje promedio
    with cols[0]:
        # CAMBIO: Eliminado * 100 porque Puntaje_Total_% ya está en porcentaje
        promedio_puntaje = df_to_display[metrics_to_display_map["Puntaje promedio"]].mean()
        st.metric("Puntaje promedio", f"{promedio_puntaje:.2f}%")

    # Muestra la Confianza promedio
    with cols[1]:
        promedio_confianza = df_to_display[metrics_to_display_map["Confianza promedio"]].mean()
        st.metric("Confianza promedio", f"{promedio_confianza:.2f}%")


    # Muestra la Polaridad promedio (como porcentaje)
    with cols[2]:
        promedio_polaridad = df_to_display[metrics_to_display_map["Polaridad promedio"]].mean()
        st.metric("Polaridad promedio", f"{promedio_polaridad:.2f}%")

    # Muestra la Subjetividad promedio (como porcentaje)
    with cols[3]:
        promedio_subjetividad = df_to_display[metrics_to_display_map["Subjetividad promedio"]].mean()
        st.metric("Subjetividad promedio", f"{promedio_subjetividad:.2f}%")

    # Muestra el Conteo de llamadas
    with cols[4]:
        conteo_llamadas = len(df_to_display) # El número de filas es el conteo de llamadas
        st.metric("Conteo llamadas", f"{conteo_llamadas}")

# ===================================================
# PASO 5: Función para gráfico de puntaje total por Agente
# ===================================================
def graficar_puntaje_total(df_to_graph):
    # Nombres de columnas actualizados
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Puntaje_Total_%' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de puntaje total. Asegúrate de tener las columnas 'Agente' y 'Puntaje_Total_%'.")
        return
    # Asegurarse de que la columna no esté vacía después de los filtros
    if df_to_graph['Puntaje_Total_%'].isnull().all():
        st.warning("⚠️ La columna 'Puntaje_Total_%' contiene solo valores nulos después de aplicar los filtros. No se puede graficar el promedio.")
        return

    # Calcular el promedio de 'Puntaje_Total_%' por 'Agente'.
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
        title="🎯 Promedio Total por Agente",
        # CAMBIO: Etiqueta de eje Y para indicar porcentaje
        labels={"Puntaje_Total_%": "Promedio de Puntaje (%)", "Agente": "Agente"}
    )
    # CAMBIO: Añadido % al formato del texto en las barras
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
    # Verificar si las columnas necesarias existen en el DataFrame (nombres actualizados)
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns or 'Polarity' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de polaridad por Agente. Asegúrate de tener las columnas 'Agente' y 'Polarity'.")
        return
    # Asegurarse de que la columna no esté vacía después de los filtros
    if df_to_graph['Polarity'].isnull().all():
        st.warning("⚠️ La columna 'Polarity' contiene solo valores nulos después de aplicar los filtros. No se puede graficar el promedio.")
        return

    # Calcular el promedio de 'Polarity' por 'Agente'.
    df_agrupado_por_agente = df_to_graph.groupby('Agente')['Polarity'].mean().reset_index()

    if df_agrupado_por_agente.empty:
        st.warning("⚠️ No hay datos para graficar el promedio de polaridad por Agente después de agrupar. Revisa tus filtros.")
        return

    # Crear gráfico de barras
    fig = px.bar(
        df_agrupado_por_agente.sort_values("Polarity", ascending=False),
        x="Agente",
        y="Polarity",
        text="Polarity",
        color="Polarity",
        color_continuous_scale="Greens", # La escala de color para el gráfico será verde
        title="📊 Polaridad Promedio por Agente",
        labels={"Polarity": "Promedio de Polaridad", "Agente": "Agente"}
    )

    # Formatear el texto y ajustar diseño
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(
        height=600,
        width=max(800, 50 * len(df_agrupado_por_agente)), # Aumenta el ancho según número de Agentes
        xaxis_tickangle=-45,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5,
        margin=dict(b=150) # Añade un margen inferior para las etiquetas de los Agentes
    )

    # Mostrar gráfico con scroll si es necesario
    st.plotly_chart(fig, use_container_width=False) # use_container_width=False permite scroll horizontal


# ===================================================
# PASO 6: Función para heatmap de métricas por Agente
# ===================================================
def graficar_asesores_metricas_heatmap(df_to_graph):
    # Nombres de columnas actualizados
    if df_to_graph is None or df_to_graph.empty or 'Agente' not in df_to_graph.columns:
        st.warning("Datos incompletos para el Heatmap. Se requiere un DataFrame con la columna 'Agente'.")
        return

    numeric_cols = df_to_graph.select_dtypes(include=['number']).columns.tolist()

    # Columnas a excluir, con nombres actualizados
    cols_to_exclude = [
        "Identificador único", "Telefono", "Puntaje_Total_%", "Polarity",
        "Subjectivity", "Confianza", "Palabras", "Oraciones", "asesor_corto" # 'asesor_corto' se mantiene si es una columna temporal.
    ]
    metric_cols = [col for col in numeric_cols if col not in cols_to_exclude]

    if not metric_cols:
        st.warning("No se encontraron columnas numéricas adecuadas para el Heatmap después de aplicar los filtros.")
        return

    # Usar 'Agente' para la agrupación.
    df_grouped = df_to_graph.groupby('Agente')[metric_cols].mean().reset_index()

    if df_grouped.empty:
        st.warning("No hay datos para mostrar en el Heatmap después de agrupar por Agente.")
        return

    df_heatmap = df_grouped.set_index("Agente")[metric_cols]

    fig2 = px.imshow(
        df_heatmap,
        labels=dict(x="Métrica", y="Agente", color="Valor"), # Etiqueta y actualizada
        color_continuous_scale='Greens',
        aspect="auto",
        title="Heatmap: Agente vs. Métricas (Promedio)"
    )
    fig2.update_layout(
        font=dict(family="Arial", size=12),
        height=700,
        title_x=0.5,
        plot_bgcolor='white'
    )
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
    with col1: # Todo lo relacionado con el primer gauge va dentro de esta columna
        st.subheader("🔍 Polaridad Promedio General")
        # Nombres de columnas actualizados
        if 'Polarity' in df_to_graph.columns and not df_to_graph['Polarity'].isnull().all():
            polaridad_total = df_to_graph['Polarity'].mean()
            
            # Aquí se crea fig_gauge, DENTRO de la condición y la columna
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
                title={'text': "Polaridad Promedio General"} # Eliminé el emoji del título para dejarlo estático
            ))
            
            # Actualizamos el layout y mostramos el gráfico aquí
            fig_gauge.update_layout(
                font=dict(family="Arial", size=16),
                width=400,  # Ancho fijo
                height=300 # Altura fija
            )
            st.plotly_chart(fig_gauge, use_container_width=False)
        else:
            st.info("No hay datos de 'Polarity' para mostrar el indicador de Polaridad.")

    # --- Gauge de Subjetividad ---
    with col2: # Todo lo relacionado con el segundo gauge va dentro de esta columna
        st.subheader("🔍 Subjectividad Promedio General")
        # Nombres de columnas actualizados
        if 'Subjectivity' in df_to_graph.columns and not df_to_graph['Subjectivity'].isnull().all():
            subjectividad_total = df_to_graph['Subjectivity'].mean()
            
            # Aquí se crea fig_gauge2, DENTRO de la condición y la columna
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
                title={'text': "Subjectividad Promedio General"} # Eliminé el emoji del título para dejarlo estático
            ))
            
            # Actualizamos el layout y mostramos el gráfico aquí
            fig_gauge2.update_layout(
                font=dict(family="Arial", size=16),
                width=400, # Ancho fijo
                height=300 # Altura fija
            )
            st.plotly_chart(fig_gauge2, use_container_width=False)
        else:
            st.info("No hay datos de 'Subjectivity' para mostrar el indicador de Subjetividad.")

# ===================================================
# PASO 8: Función para mostrar busbujas
# ===================================================      
def graficar_polaridad_confianza_asesor_burbujas(df_to_graph):
    # Verificar si las columnas necesarias existen en el DataFrame (nombres actualizados)
    if df_to_graph is None or df_to_graph.empty or \
       'Agente' not in df_to_graph.columns or \
       'Polarity' not in df_to_graph.columns or \
       'Confianza' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de burbujas. Asegúrate de tener las columnas 'Agente', 'Polarity' y 'Confianza'.")
        return
    # Asegurarse de que las columnas no estén vacías después de los filtros
    if df_to_graph['Polarity'].isnull().all() or df_to_graph['Confianza'].isnull().all():
        st.warning("⚠️ Las columnas 'Polarity' o 'Confianza' contienen solo valores nulos después de aplicar los filtros. No se puede graficar el promedio.")
        return


    # 1. Agrupar por 'Agente' y calcular promedios de polaridad y confianza
    # 2. Contar el número de registros/llamadas por Agente
    # Nombres de columnas actualizados
    df_agrupado_por_agente = df_to_graph.groupby('Agente').agg(
        promedio_polaridad=('Polarity', 'mean'),
        promedio_confianza=('Confianza', 'mean'),
        numero_llamadas=('Agente', 'count') # Cuenta el número de filas por Agente
    ).reset_index()

    if df_agrupado_por_agente.empty:
        st.warning("⚠️ No hay datos para graficar la polaridad vs. confianza por Agente después de agrupar. Revisa tus filtros.")
        return

    # Crear el gráfico de burbujas
    fig = px.scatter(
        df_agrupado_por_agente,
        x="promedio_polaridad",         # Eje X: Polaridad Promedio
        y="promedio_confianza",         # Eje Y: Confianza Promedio
        size="numero_llamadas",         # Tamaño de la burbuja: Número de Llamadas
        color="promedio_polaridad",     # Color de la burbuja: Basado en el valor de polaridad promedio
        color_continuous_scale="Greens",
        hover_name="Agente",            # Muestra el nombre del Agente al pasar el mouse
        log_x=False,                    # No escalar logarítmicamente el eje X
        size_max=60,                    # Tamaño máximo para las burbujas más grandes (ajustable)
        title="📊 Polaridad Promedio vs. Confianza Promedio por Agente (Tamaño = # Llamadas)",
        labels={
            "promedio_polaridad": "Polaridad Promedio",
            "promedio_confianza": "Confianza Promedio",
            "numero_llamadas": "Número de Llamadas"
        }
    )

    # Ajustar el diseño del gráfico
    fig.update_layout(
        height=600,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5,
        xaxis=dict(range=[-0.2, 0.5]), # Rango fijo para polaridad
        yaxis=dict(range=[0.6, 1])    # Rango fijo para confianza (asumiendo de 0 a 1)
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)      

# ===================================================
# PASO 8: Función para mostrar acordeones por Agente
# ===================================================
def mostrar_acordeones(df_to_display):
    if df_to_display is None or df_to_display.empty:
        st.warning("⚠️ El DataFrame está vacío o no fue cargado correctamente.")
        return
    # Nombre de columna actualizado
    if 'Agente' not in df_to_display.columns:
        st.error("❌ El DataFrame no contiene la columna 'Agente'.")
        return

    st.markdown("### 🔍 Detalle Completo por Agente")

    # Asegurar que la columna 'Agente' sea de tipo string.
    df_to_display['Agente'] = df_to_display['Agente'].astype(str)
    unique_agentes = df_to_display['Agente'].dropna().unique()

    # Columnas a excluir, con nombres actualizados
    cols_to_exclude_from_accordion = [
        "Identificador único", "Telefono", "Puntaje_Total_%", "Polarity",
        "Subjectivity", "Confianza", "Palabras", "Oraciones",
        "asesor_corto", "fecha_convertida" # 'asesor_corto' se mantiene si es una columna temporal.
    ]

    for nombre_agente in unique_agentes:
        # Nombre de columna actualizado
        df_agente = df_to_display[df_to_display['Agente'] == nombre_agente]

        with st.expander(f"🧑 Detalle de: **{nombre_agente}**"):
            for index, row in df_agente.iterrows():
                # Nombre de columna actualizado
                archivo = row.get("Archivo_Analizado", "Archivo desconocido")
                st.write(f"📄 Analizando: **{archivo}**")

                for col in df_to_display.columns:
                    # Nombres de columnas actualizados
                    if col in cols_to_exclude_from_accordion or col in ['Agente', 'Archivo_Analizado']:
                        continue

                    valor = row.get(col, 'N/A')

                    if pd.isna(valor):
                        st.write(f"🔹 {col.replace('_', ' ').capitalize()}: N/A ❌ (sin dato)")
                        continue

                    cumple = '❌'
                    if isinstance(valor, (int, float)):
                        # Nombres de columnas actualizados
                        if 'Puntaje_Total_%' in col or '%' in col: # Se asume que el porcentaje está en el nombre de la columna
                            cumple = '✅' if valor >= 80 else '❌'
                        elif 'Conteo_saludo_inicial' in col or 'Conteo_identificacion_cliente' in col or \
                             'Conteo_comprension_problema' in col or 'Conteo_ofrecimiento_solucion' in col or \
                             'Conteo_manejo_inquietudes' in col or 'Conteo_cierre_servicio' in col or \
                             'Conteo_proximo_paso' in col:
                            cumple = '✅' if valor >= 1 else '❌'
                        else:
                            cumple = '✅'
                    st.write(f"🔹 {col.replace('_', ' ').capitalize()}: {valor} {cumple}")

                if len(df_agente) > 1 and index < len(df_agente) - 1:
                    st.markdown("---")

# ===================================================
# PASO 9: Función principal de la aplicación (main)
# ===================================================
def main():
    st.sidebar.header("Filtros")

    # --- FILTRO POR AGENTE ---
    # Nombre de columna actualizado
    # Verificar si 'Agente' existe y no está completamente vacío antes de intentar obtener únicos.
    if 'Agente' in df.columns and not df['Agente'].dropna().empty:
        asesores = ["Todos"] + sorted(df["Agente"].dropna().unique())
    else:
        asesores = ["Todos"] # Si no hay datos de Agente, solo ofrecer 'Todos'
        st.sidebar.warning("⚠️ No se encontraron agentes en los datos. El filtro de Agente estará limitado.")

    asesor_seleccionado = st.sidebar.selectbox("👤 Selecciona un Agente", asesores)

    df_filtrado = df.copy() # Siempre empezamos con una copia del DF original

    if asesor_seleccionado != "Todos":
        # Nombre de columna actualizado
        df_filtrado = df_filtrado[df_filtrado["Agente"] == asesor_seleccionado].copy()

    # --- FILTRO POR FECHA ---
    # **** INICIO DE LA SECCIÓN CLAVE PARA TU FILTRO DE FECHA ****
    st.sidebar.markdown("---") # Separador visual para el filtro de fecha

    if 'fecha_convertida' in df_filtrado.columns:
        # Debug: Verificar cuántos valores no nulos hay en la columna de fechas
        num_fechas_no_nulas = df_filtrado['fecha_convertida'].dropna().shape[0]
        st.sidebar.write(f"📊 Total de registros con fecha_convertida no nula (después de filtro de Agente): {num_fechas_no_nulas}")

        if not df_filtrado['fecha_convertida'].dropna().empty:
            fechas_validas = df_filtrado['fecha_convertida'].dropna().dt.date.unique()
            fechas_ordenadas = sorted(fechas_validas)
            opciones_fechas = ["Todos"] + [str(fecha) for fecha in fechas_ordenadas]

            # Debug: Mostrar las fechas que se están usando para el SelectBox
            st.sidebar.write(f"📅 Fechas detectadas para el filtro: {len(fechas_ordenadas)} únicas.")
            # st.sidebar.write(f"Ejemplo de fechas: {fechas_ordenadas[:5]}") # Muestra las primeras 5 fechas

            fecha_seleccionada = st.sidebar.selectbox("📅 **Filtrar por fecha exacta**", opciones_fechas)

            if fecha_seleccionada != "Todos":
                try:
                    fecha_filtrada_dt = pd.to_datetime(fecha_seleccionada).date()
                    # Aquí se aplica el filtro de fecha final
                    df_filtrado = df_filtrado[df_filtrado['fecha_convertida'].dt.date == fecha_filtrada_dt]
                except Exception as e:
                    st.sidebar.error(f"❌ Error al filtrar por la fecha seleccionada: {e}")
            else:
                st.sidebar.info("Mostrando datos de todas las fechas disponibles.")
        else:
            st.sidebar.warning("⚠️ No hay fechas válidas en los datos filtrados para mostrar un selector.")
            # Debug: Revisa si df_filtrado está vacío aquí
            # st.sidebar.write(f"¿df_filtrado vacío en esta etapa? {df_filtrado.empty}")
            # st.sidebar.write("Contenido de fecha_convertida antes del filtro de fecha:", df_filtrado['fecha_convertida'].head())
    else:
        st.sidebar.error("❌ La columna 'fecha_convertida' no existe en el DataFrame filtrado.")
        # Debug: Mostrar las columnas disponibles
        # st.sidebar.write("Columnas disponibles:", df_filtrado.columns.tolist())

    # **** FIN DE LA SECCIÓN CLAVE PARA TU FILTRO DE FECHA ****
    st.sidebar.markdown("---") # Separador final para los filtros


    # El resto de tu código para mostrar métricas y gráficos permanece igual
    st.title("📊 Dashboard de Análisis Cartera")

    if df_filtrado.empty:
        st.warning("🚨 ¡Atención! No hay datos para mostrar con los filtros seleccionados. Ajusta tus filtros.")
        return

    display_summary_metrics(df_filtrado)
    st.markdown("---")

    st.header("📈 Gráficos Resumen")
    # st.write("Columnas actuales en df_filtrado:", df_filtrado.columns.tolist()) # Línea de debug

    graficar_puntaje_total(df_filtrado)
    st.markdown("---")

    graficar_polaridad_asesor_total(df_filtrado) # El nombre de la función se mantiene, pero usa 'Agente' internamente
    st.markdown("---")

    graficar_asesores_metricas_heatmap(df_filtrado)
    st.markdown("---")

    graficar_polaridad_subjetividad_gauges(df_filtrado)
    st.markdown("---")
    graficar_polaridad_confianza_asesor_burbujas(df_filtrado)
    st.markdown("---")
    mostrar_acordeones(df_filtrado)

# ===================================================
# PASO 10: Punto de entrada de la app
# ===================================================
if __name__ == '__main__':
    main()
