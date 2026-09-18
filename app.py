import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# ----------------------------------------
# 1. Configuración de la página
# ----------------------------------------
st.set_page_config(
    page_title="SIATA - Calidad del Aire (PM2.5)",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados (CSS inyectado)
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        color: white;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# 2. Carga y limpieza de datos (Caché)
# ----------------------------------------
@st.cache_data(ttl=300) # Caché por 5 minutos
def load_data():
    url = "https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_AQ_pm25_Last.json"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        datos_raw = response.json()
        
        # Extraer mediciones
        if 'measurements' in datos_raw:
            df = pd.json_normalize(datos_raw, record_path='measurements')
        else:
            df = pd.DataFrame(datos_raw)
            
        # Limpieza: Filtrar -9999 (No disponible)
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df[df['value'] != -9999].copy()
            
        # Asegurar columnas de coordenadas
        if 'latitude' not in df.columns and 'coordinates.latitude' in df.columns:
            df['latitude'] = df['coordinates.latitude']
            df['longitude'] = df['coordinates.longitude']
            
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Eliminar filas sin coordenadas si vamos a mapear
        df = df.dropna(subset=['latitude', 'longitude', 'value', 'location'])
        
        # Convertir fechas
        if 'date.local' in df.columns:
            df['date.local'] = pd.to_datetime(df['date.local'], errors='coerce')
            
        # Determinar nivel de riesgo (ICA simplificado PM2.5)
        def get_risk_level(val):
            if val <= 12: return 'Bueno'
            elif val <= 35: return 'Moderado'
            elif val <= 55.4: return 'Dañino grupos sensibles'
            else: return 'Dañino / Peligroso'
            
        df['Riesgo'] = df['value'].apply(get_risk_level)
        
        return df
    except Exception as e:
        st.error(f"Error al descargar los datos: {e}")
        return pd.DataFrame()

df = load_data()

# ----------------------------------------
# 3. Sidebar (Filtros e Interacción)
# ----------------------------------------
st.sidebar.image("https://siata.gov.co/sitio_web/images/logo_siata.png", width=150)
st.sidebar.title("Filtros de Análisis")
st.sidebar.write("Selecciona los parámetros para explorar los datos.")

if not df.empty:
    # Filtro por Estación
    estaciones_disponibles = ['Todas'] + sorted(df['location'].unique().tolist())
    estacion_seleccionada = st.sidebar.selectbox("Selecciona una Estación", estaciones_disponibles)

    # Filtro por Nivel de Riesgo
    riesgos_disponibles = ['Todos'] + sorted(df['Riesgo'].unique().tolist())
    riesgo_seleccionado = st.sidebar.selectbox("Filtrar por Nivel de Riesgo", riesgos_disponibles)

    # Aplicar filtros
    df_filtrado = df.copy()
    if estacion_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['location'] == estacion_seleccionada]
    
    if riesgo_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Riesgo'] == riesgo_seleccionado]
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"Mostrando **{len(df_filtrado)}** registros tras aplicar filtros.")
else:
    st.warning("No hay datos disponibles para procesar.")
    st.stop()


# ----------------------------------------
# 4. Cuerpo Principal (Dashboard)
# ----------------------------------------
st.title("📊 Monitor de Calidad del Aire (PM2.5)")
st.markdown("Datos oficiales del **Sistema de Alerta Temprana de Medellín y el Valle de Aburrá (SIATA)**.")

# --- Métricas ---
col1, col2, col3 = st.columns(3)
with col1:
    promedio_pm25 = df_filtrado['value'].mean()
    st.metric(label="Promedio PM2.5 (µg/m³)", value=f"{promedio_pm25:.2f}" if pd.notna(promedio_pm25) else "N/A")

with col2:
    if not df_filtrado.empty:
        max_row = df_filtrado.loc[df_filtrado['value'].idxmax()]
        st.metric(label="Valor Máximo Detectado", value=f"{max_row['value']:.1f}", delta=max_row['location'], delta_color="inverse")
    else:
        st.metric(label="Valor Máximo Detectado", value="N/A")

with col3:
    st.metric(label="Estaciones Analizadas", value=len(df_filtrado['location'].unique()))

st.markdown("---")

# --- Layout Visualizaciones ---
col_grafico, col_mapa = st.columns((5, 5))

with col_grafico:
    st.subheader("📈 Top Estaciones con Mayor Contaminación")
    
    if not df_filtrado.empty:
        # Agrupar para grafico
        top_estaciones = df_filtrado.groupby('location', as_index=False)['value'].mean().sort_values('value', ascending=False).head(10)
        
        fig_bar = px.bar(
            top_estaciones,
            x='value',
            y='location',
            orientation='h',
            title='Top 10 PM2.5 Promedio',
            labels={'value': 'PM2.5 (µg/m³)', 'location': 'Estación'},
            color='value',
            color_continuous_scale=px.colors.sequential.Reds
        )
        # Añadir linea de limite OMS
        fig_bar.add_vline(x=15, line_dash="dash", line_color="red", annotation_text="Límite OMS (15)")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=450)
        
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("No hay datos para graficar con los filtros actuales.")

with col_mapa:
    st.subheader("📍 Mapa de Estaciones (Último Reporte)")
    
    if not df_filtrado.empty:
        # Usamos Plotly Express para el mapa
        # Color mapping para el riesgo
        color_map = {
            'Bueno': '#10b981',
            'Moderado': '#f59e0b',
            'Dañino grupos sensibles': '#ef4444',
            'Dañino / Peligroso': '#7f1d1d'
        }
        
        fig_map = px.scatter_mapbox(
            df_filtrado, 
            lat="latitude", 
            lon="longitude", 
            hover_name="location", 
            hover_data={"value": True, "Riesgo": True, "latitude": False, "longitude": False},
            color="Riesgo",
            color_discrete_map=color_map,
            size="value",
            size_max=15,
            zoom=10, 
            height=450,
            title="Distribución Geográfica de PM2.5"
        )
        fig_map.update_layout(mapbox_style="carto-darkmatter")
        fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("No hay datos para mapear con los filtros actuales.")

# --- Tabla de datos ---
with st.expander("Ver tabla de datos crudos"):
    st.dataframe(df_filtrado[['location', 'value', 'unit', 'Riesgo', 'date.local', 'latitude', 'longitude']].sort_values('value', ascending=False))
