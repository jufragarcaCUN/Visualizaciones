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
archivo_principal = carpeta_base / "reporte_completo_con_celular_ventas_fecha_corregida.xlsx"

# Cargar el archivo Excel en un DataFrame de pandas.
try:
    df = pd.read_excel(archivo_principal)
except FileNotFoundError:
    st.error(f"Error: El archivo no se encontró en la ruta especificada: {archivo_principal}")
    st.stop() # Detiene la ejecución de la aplicación si el archivo no se encuentra.

# Configurar la configuración regional a español para el formato de fechas.
# Esto es crucial para que `pd.to_datetime` pueda interpretar nombres de meses en español.
#try:
    #locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
#except locale.Error:
    st.warning("No se pudo establecer la configuración regional 'es_ES.UTF-8'. La conversión de fechas con nombres de meses en español podría fallar. Asegúrese de que el entorno soporte esta configuración regional.")
    # Intenta con una alternativa común para sistemas Windows si la anterior falla
    #try:
        #locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    #except locale.Error:
        #st.warning("No se pudo establecer la configuración regional 'Spanish_Spain.1252' tampoco. La conversión de fechas podría ser inconsistente.")


# Convertir la columna 'fecha' a formato de fecha y hora, manejando errores.
# Se usa un formato explícito para "Junio 10 de 2025".
df['fecha_convertida'] = pd.to_datetime(df['fecha'], format='%B %d de %Y', errors='coerce')

# Asegurarse de que 'asesor' sea de tipo string para evitar errores en agrupaciones/filtros.
if 'asesor' in df.columns:
    df['asesor'] = df['asesor'].astype(str)

# ===================================================
# PASO 4: Función para mostrar métricas resumen
# ===================================================
import streamlit as st
import pandas as pd

def display_summary_metrics(df_to_display):
    st.markdown("## 📋 Resumen General de Métricas")

    # Define las métricas exactas que quieres mostrar y sus nombres de columna correspondientes
    # en el DataFrame.
    # Es crucial que 'puntaje', 'confianza', 'polarity', y 'subjectivity' sean los nombres reales de tus columnas.
    metrics_to_display_map = {
        "Puntaje promedio": "puntaje",
        "Confianza promedio": "confianza",
        "Polaridad promedio": "polarity",
        "Subjetividad promedio": "subjectivity",
    }

    # Verifica si el DataFrame contiene todas las columnas necesarias
    for display_name, col_name in metrics_to_display_map.items():
        if col_name not in df_to_display.columns:
            st.warning(f"⚠️ La columna '{col_name}' necesaria para '{display_name}' no se encontró en los datos. Por favor, verifica el nombre de la columna.")
            return

    # Crea las columnas en Streamlit para mostrar las métricas
    # Necesitamos 5 columnas: 4 para los promedios y 1 para el conteo de llamadas.
    cols = st.columns(5)

    # Muestra el Puntaje promedio
    promedio_puntaje = df_to_display[metrics_to_display_map["Puntaje promedio"]].mean() # Aquí no se multiplica por 100
        st.metric("Puntaje promedio", f"{promedio_puntaje:.2f}") # Aquí no se añade "%"

    # Muestra la Confianza promedio
    promedio_confianza = df_to_display[metrics_to_display_map["Confianza promedio"]].mean()*100 # ¡Aquí sí se multiplica por 100!
        st.metric("Confianza promedio", f"{promedio_confianza:.2f}%") # ¡Aquí sí se añade "%"!")

    # Muestra la Polaridad promedio (como porcentaje)
    with cols[2]:
        promedio_polaridad = df_to_display[metrics_to_display_map["Polaridad promedio"]].mean() * 100
        st.metric("Polaridad promedio", f"{promedio_polaridad:.2f}%")

    # Muestra la Subjetividad promedio (como porcentaje)
    with cols[3]:
        promedio_subjetividad = df_to_display[metrics_to_display_map["Subjetividad promedio"]].mean() * 100
        st.metric("Subjetividad promedio", f"{promedio_subjetividad:.2f}%")

    # Muestra el Conteo de llamadas
    with cols[4]:
        conteo_llamadas = len(df_to_display) # El número de filas es el conteo de llamadas
        st.metric("Conteo llamadas", f"{conteo_llamadas}")# ===================================================
# PASO 5: Función para gráfico de puntaje total por asesor
# ===================================================
def graficar_puntaje_total(df_to_graph):
    if df_to_graph is None or df_to_graph.empty or 'asesor' not in df_to_graph.columns or 'puntaje' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de puntaje total. Asegúrate de tener las columnas 'asesor' y 'puntaje'.")
        return

    # Calcular el promedio de 'puntaje' por 'asesor'.
    df_agrupado_por_asesor = df_to_graph.groupby('asesor')['puntaje'].mean().reset_index()

    if df_agrupado_por_asesor.empty:
        st.warning("⚠️ No hay datos para graficar el promedio total por asesor después de agrupar. Revisa tus filtros.")
        return

    fig = px.bar(
        df_agrupado_por_asesor.sort_values("puntaje", ascending=False),
        x="asesor",
        y="puntaje",
        text="puntaje",
        color="puntaje",
        color_continuous_scale="Greens",
        title="🎯 Promedio Total por Asesor",
        labels={"puntaje": "Promedio de Puntaje", "asesor": "Asesor"}
    )
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(
        height=600,
        xaxis_tickangle=-45,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)

# ===================================================
# Función para gráfico de polaridad por asesor
# ===================================================
def graficar_polaridad_asesor_total(df_to_graph):
    # Verificar si las columnas necesarias existen en el DataFrame
    if df_to_graph is None or df_to_graph.empty or 'asesor' not in df_to_graph.columns or 'polarity' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de polaridad por asesor. Asegúrate de tener las columnas 'asesor' y 'polarity'.")
        return

    # Calcular el promedio de 'polarity' por 'asesor'.
    df_agrupado_por_asesor = df_to_graph.groupby('asesor')['polarity'].mean().reset_index()

    # Verificar si el DataFrame agrupado está vacío
    if df_agrupado_por_asesor.empty: # Corregida la variable aquí
        st.warning("⚠️ No hay datos para graficar el promedio de polaridad por asesor después de agrupar. Revisa tus filtros.")
        return

    # Crear gráfico de barras
    fig = px.bar(
        df_agrupado_por_asesor.sort_values("polarity", ascending=False),
        x="asesor",
        y="polarity",
        text="polarity",
        color="polarity",
        color_continuous_scale="Greens", # La escala de color para el gráfico será verde
        title="📊 Polaridad Promedio por Asesor",
        labels={"polarity": "Promedio de Polaridad", "asesor": "Asesor"}
    )

    # Formatear el texto y ajustar diseño
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(
        height=600,
        width=max(800, 50 * len(df_agrupado_por_asesor)), # Aumenta el ancho según número de asesores
        xaxis_tickangle=-45,
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        title_x=0.5,
        margin=dict(b=150) # Añade un margen inferior para las etiquetas de los asesores
    )

    # Mostrar gráfico con scroll si es necesario
    st.plotly_chart(fig, use_container_width=False) # use_container_width=False permite scroll horizontal


# ===================================================
# PASO 6: Función para heatmap de métricas por asesor
# ===================================================
def graficar_asesores_metricas_heatmap(df_to_graph):
    if df_to_graph is None or df_to_graph.empty or 'asesor' not in df_to_graph.columns:
        st.warning("Datos incompletos para el Heatmap. Se requiere un DataFrame con la columna 'asesor'.")
        return

    numeric_cols = df_to_graph.select_dtypes(include=['number']).columns.tolist()

    cols_to_exclude = [
        "id_", "celular", "puntaje", "polarity",
        "subjectivity", "confianza", "palabras", "oraciones"
    ]
    metric_cols = [col for col in numeric_cols if col not in cols_to_exclude]

    if not metric_cols:
        st.warning("No se encontraron columnas numéricas adecuadas para el Heatmap después de aplicar los filtros.")
        return

    # Usar 'asesor' para la agrupación. Si 'asesor_corto' es una columna real, úsala.
    # De lo contrario, puedes crear una versión corta si es necesario.
    # Por simplicidad y consistencia, usaremos 'asesor' directamente.
    df_grouped = df_to_graph.groupby('asesor')[metric_cols].mean().reset_index()

    if df_grouped.empty:
        st.warning("No hay datos para mostrar en el Heatmap después de agrupar por asesor.")
        return

    df_heatmap = df_grouped.set_index("asesor")[metric_cols]

    fig2 = px.imshow(
        df_heatmap,
        labels=dict(x="Métrica", y="Asesor", color="Valor"),
        color_continuous_scale='Greens',
        aspect="auto",
        title="Heatmap: Asesor vs. Métricas (Promedio)"
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
        if 'polarity' in df_to_graph.columns and not df_to_graph['polarity'].isnull().all():
            polaridad_total = df_to_graph['polarity'].mean()
            
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
            st.info("No hay datos de 'polarity' para mostrar el indicador de Polaridad.")

    # --- Gauge de Subjetividad ---
    with col2: # Todo lo relacionado con el segundo gauge va dentro de esta columna
        st.subheader("🔍 Subjectividad Promedio General")
        if 'subjectivity' in df_to_graph.columns and not df_to_graph['subjectivity'].isnull().all():
            subjectividad_total = df_to_graph['subjectivity'].mean()
            
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
            st.info("No hay datos de 'subjectivity' para mostrar el indicador de Subjetividad.")
# ===================================================
# PASO 8: Función para mostrar busbujas
# ===================================================      
# import plotly.express as px
import pandas as pd
import streamlit as st

def graficar_polaridad_confianza_asesor_burbujas(df_to_graph):
    # Verificar si las columnas necesarias existen en el DataFrame
    if df_to_graph is None or df_to_graph.empty or \
       'asesor' not in df_to_graph.columns or \
       'polarity' not in df_to_graph.columns or \
       'confianza' not in df_to_graph.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de burbujas. Asegúrate de tener las columnas 'asesor', 'polarity' y 'confianza'.")
        return

    # 1. Agrupar por 'asesor' y calcular promedios de polaridad y confianza
    # 2. Contar el número de registros/llamadas por asesor
    df_agrupado_por_asesor = df_to_graph.groupby('asesor').agg(
        promedio_polaridad=('polarity', 'mean'),
        promedio_confianza=('confianza', 'mean'),
        numero_llamadas=('asesor', 'count') # Cuenta el número de filas por asesor
    ).reset_index()

    if df_agrupado_por_asesor.empty:
        st.warning("⚠️ No hay datos para graficar la polaridad vs. confianza por asesor después de agrupar. Revisa tus filtros.")
        return

    # Crear el gráfico de burbujas
    fig = px.scatter(
        df_agrupado_por_asesor,
        x="promedio_polaridad",       # Eje X: Polaridad Promedio
        y="promedio_confianza",       # Eje Y: Confianza Promedio
        size="numero_llamadas",       # Tamaño de la burbuja: Número de Llamadas
        color="promedio_polaridad",   # Color de la burbuja: Basado en el valor de polaridad promedio
        color_continuous_scale="Greens",
        hover_name="asesor",          # Muestra el nombre del asesor al pasar el mouse
        log_x=False,                  # No escalar logarítmicamente el eje X
        size_max=60,                  # Tamaño máximo para las burbujas más grandes (ajustable)
        title="📊 Polaridad Promedio vs. Confianza Promedio por Asesor (Tamaño = # Llamadas)",
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
        yaxis=dict(range=[0.6, 1])   # Rango fijo para confianza (asumiendo de 0 a 1)
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)      
# ===================================================
# PASO 8: Función para mostrar acordeones por asesor
# ===================================================
def mostrar_acordeones(df_to_display):
    if df_to_display is None or df_to_display.empty:
        st.warning("⚠️ El DataFrame está vacío o no fue cargado correctamente.")
        return
    if 'asesor' not in df_to_display.columns:
        st.error("❌ El DataFrame no contiene la columna 'asesor'.")
        return

    st.markdown("### 🔍 Detalle Completo por Asesor")

    # Asegurar que la columna 'asesor' sea de tipo string. (ya se hizo globalmente, pero no está de más en funciones)
    df_to_display['asesor'] = df_to_display['asesor'].astype(str)
    unique_asesores = df_to_display['asesor'].dropna().unique()

    cols_to_exclude_from_accordion = [
        "id_", "celular", "puntaje", "polarity",
        "subjectivity", "confianza", "palabras", "oraciones",
        "asesor_corto", "fecha_convertida" # Excluir tambien la columna de fecha convertida
    ]

    for nombre_asesor in unique_asesores:
        df_asesor = df_to_display[df_to_display['asesor'] == nombre_asesor]

        with st.expander(f"🧑 Detalle de: **{nombre_asesor}**"):
            for index, row in df_asesor.iterrows():
                archivo = row.get("archivo", "Archivo desconocido")
                st.write(f"📄 Analizando: **{archivo}**")

                for col in df_to_display.columns:
                    if col in cols_to_exclude_from_accordion or col in ['asesor', 'archivo']:
                        continue

                    valor = row.get(col, 'N/A')

                    if pd.isna(valor):
                        st.write(f"🔹 {col.replace('_', ' ').capitalize()}: N/A ❌ (sin dato)")
                        continue

                    cumple = '❌'
                    if isinstance(valor, (int, float)):
                        if 'puntaje' in col or '%' in col:
                            cumple = '✅' if valor >= 80 else '❌'
                        elif 'conteo' in col or 'saludo' in col or 'cierre' in col:
                            cumple = '✅' if valor >= 1 else '❌'
                        else:
                            cumple = '✅'
                    st.write(f"🔹 {col.replace('_', ' ').capitalize()}: {valor} {cumple}")

                if len(df_asesor) > 1 and index < len(df_asesor) - 1:
                    st.markdown("---")

# ===================================================
# PASO 9: Función principal de la aplicación (main)
# ===================================================
def main():
    st.sidebar.header("Filtros")

    # --- FILTRO POR ASESOR ---
    asesores = ["Todos"] + sorted(df["asesor"].dropna().unique())
    asesor_seleccionado = st.sidebar.selectbox("👤 Selecciona un asesor", asesores)

    df_filtrado = df.copy() # Siempre empezamos con una copia del DF original

    if asesor_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["asesor"] == asesor_seleccionado].copy()

    # --- FILTRO POR FECHA ---
    # **** INICIO DE LA SECCIÓN CLAVE PARA TU FILTRO DE FECHA ****
    st.sidebar.markdown("---") # Separador visual para el filtro de fecha

    if 'fecha_convertida' in df_filtrado.columns:
        # Debug: Verificar cuántos valores no nulos hay en la columna de fechas
        num_fechas_no_nulas = df_filtrado['fecha_convertida'].dropna().shape[0]
        st.sidebar.write(f"📊 Total de registros con fecha_convertida no nula (después de filtro de asesor): {num_fechas_no_nulas}")

        if not df_filtrado['fecha_convertida'].dropna().empty:
            fechas_validas = df_filtrado['fecha_convertida'].dropna().dt.date.unique()
            fechas_ordenadas = sorted(fechas_validas)
            opciones_fechas = ["Todas"] + [str(fecha) for fecha in fechas_ordenadas]

            # Debug: Mostrar las fechas que se están usando para el SelectBox
            st.sidebar.write(f"📅 Fechas detectadas para el filtro: {len(fechas_ordenadas)} únicas.")
            # st.sidebar.write(f"Ejemplo de fechas: {fechas_ordenadas[:5]}") # Muestra las primeras 5 fechas

            fecha_seleccionada = st.sidebar.selectbox("📅 **Filtrar por fecha exacta**", opciones_fechas)

            if fecha_seleccionada != "Todas":
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
    st.title("📊 Dashboard de Análisis de Ventas")

    if df_filtrado.empty:
        st.warning("🚨 ¡Atención! No hay datos para mostrar con los filtros seleccionados. Ajusta tus filtros.")
        return

    display_summary_metrics(df_filtrado)
    st.markdown("---")

    st.header("📈 Gráficos Resumen")
    # st.write("Columnas actuales en df_filtrado:", df_filtrado.columns.tolist()) # Línea de debug

    graficar_puntaje_total(df_filtrado)
    st.markdown("---")

    graficar_polaridad_asesor_total(df_filtrado)
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
