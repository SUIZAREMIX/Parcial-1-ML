# 🌬️ SIATA Air Quality Streamlit App

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.2.1-150458.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.19.0-3f4f75.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

Esta es una aplicación interactiva construida con [Streamlit](https://streamlit.io/) que consume, limpia y visualiza los datos en tiempo real de PM2.5 provenientes de la red de monitoreo del **SIATA** (Sistema de Alerta Temprana de Medellín y el Valle de Aburrá).

## ✨ Características

- **Consumo en tiempo real:** Extrae los últimos datos del endpoint oficial del SIATA.
- **Filtrado Inteligente:** Elimina automáticamente registros no válidos (errores `-9999`).
- **Dashboard Interactivo:**
  - Métricas clave globales (Promedio PM2.5, Estación más crítica).
  - Selector de estación para análisis detallado.
  - Gráfico de barras interactivo del Top 10 de estaciones más contaminadas usando Plotly.
  - Mapa interactivo de calor para ubicar las estaciones con altos niveles de riesgo.

## 🚀 Despliegue Rápido (Local)

Sigue estos pasos para ejecutar la aplicación en tu entorno local:

1. **Clona el repositorio** o asegúrate de estar en el directorio `streamlit_app`.
2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ejecuta la aplicación**:
   ```bash
   streamlit run app.py
   ```
4. **Visualiza en el navegador**: La aplicación se abrirá automáticamente en `http://localhost:8501`.

## ☁️ Despliegue en Streamlit Community Cloud

Esta aplicación está completamente lista para ser desplegada en [Streamlit Community Cloud](https://share.streamlit.io/):
1. Sube este directorio (`streamlit_app`) a un repositorio público en GitHub.
2. Inicia sesión en Streamlit Cloud y crea una "New App".
3. Selecciona tu repositorio, rama y apunta al archivo principal `app.py`.
4. ¡Listo! Streamlit instalará las dependencias de `requirements.txt` y desplegará tu app públicamente.

---
*Desarrollado como prueba técnica de Machine Learning y Análisis de Datos.*
