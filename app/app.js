const SIATA_API_URL = "https://siata.gov.co/EntregaData1/Datos_SIATA_Aire_AQ_pm25_Last.json";
let map;
let markersLayer;

// Limites OMS e ICA aproximado para PM2.5 (simplificado)
const getColorForPM25 = (value) => {
    if (value <= 12) return '#10b981'; // Bueno
    if (value <= 35) return '#f59e0b'; // Moderado
    if (value <= 55.4) return '#ef4444'; // Dañino para grupos sensibles / Dañino
    return '#7f1d1d'; // Muy Dañino / Peligroso
};

const getTextColorClass = (value) => {
    if (value <= 12) return 'val-good';
    if (value <= 35) return 'val-moderate';
    return 'val-unhealthy';
};

// Inicializar Mapa
const initMap = () => {
    // Coordenadas centrales de Medellín
    map = L.map('map').setView([6.2442, -75.5812], 11);
    
    // Capa base oscura (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);
};

// Cargar y procesar datos
const loadData = async () => {
    const btnRefresh = document.getElementById('refreshData');
    btnRefresh.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Actualizando...';
    btnRefresh.disabled = true;

    try {
        const response = await fetch(SIATA_API_URL);
        if (!response.ok) throw new Error("Error en la respuesta de red");
        
        const dataRaw = await response.json();
        
        // Asumiendo que la estructura es parecida a lo visto en siata.py: datos_raw['measurements'] o es una lista directa.
        // En siata.py hace: df = pd.json_normalize(datos_raw, record_path='measurements')
        // Por si acaso iteramos sobre la lista si dataRaw ya es la lista, o dataRaw.measurements.
        let measurements = Array.isArray(dataRaw) ? dataRaw : (dataRaw.measurements || []);

        // 1. Filtrar -9999
        let validData = measurements.filter(item => item.value !== -9999);
        
        // 2. Agrupar por ubicación para sacar el promedio si hay múltiples lecturas,
        // o simplemente tomar el último dato válido por estación si el endpoint da la última foto.
        // Dado el endpoint "...Last.json", parece ser el último valor de cada estación.
        // Haremos un map directo para estaciones únicas, usando su location como clave.
        const stations = {};
        
        validData.forEach(item => {
            if(!stations[item.location]) {
                stations[item.location] = {
                    name: item.location,
                    lat: item.latitude || (item.coordinates && item.coordinates.latitude),
                    lon: item.longitude || (item.coordinates && item.coordinates.longitude),
                    value: parseFloat(item.value),
                    date: item["date.local"] || item.date || new Date().toLocaleString()
                };
            }
        });

        const stationsArray = Object.values(stations);
        
        // Renderizar Mapa
        updateMap(stationsArray);
        
        // Renderizar Top 10
        updateSidebar(stationsArray);

    } catch (error) {
        console.error("Error cargando datos:", error);
        document.getElementById('stationsList').innerHTML = `<p style="color:red"><i class="fa-solid fa-triangle-exclamation"></i> Error al cargar los datos del SIATA. Intenta nuevamente.</p>`;
    } finally {
        btnRefresh.innerHTML = '<i class="fa-solid fa-rotate"></i> Actualizar';
        btnRefresh.disabled = false;
    }
};

const updateMap = (stations) => {
    markersLayer.clearLayers();
    
    stations.forEach(st => {
        if (st.lat && st.lon) {
            const color = getColorForPM25(st.value);
            
            const markerOptions = {
                radius: 8,
                fillColor: color,
                color: "#fff",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            };
            
            const popupContent = `
                <div style="color: black;">
                    <strong>${st.name}</strong><br>
                    PM2.5: ${st.value} µg/m³<br>
                    <em>${st.date}</em>
                </div>
            `;
            
            L.circleMarker([st.lat, st.lon], markerOptions)
                .bindPopup(popupContent)
                .addTo(markersLayer);
        }
    });
};

const updateSidebar = (stations) => {
    // Ordenar de mayor a menor PM2.5 y tomar el top 10
    const top10 = [...stations].sort((a, b) => b.value - a.value).slice(0, 10);
    
    const container = document.getElementById('stationsList');
    container.innerHTML = '';
    
    if (top10.length === 0) {
        container.innerHTML = '<p>No hay datos disponibles en este momento.</p>';
        return;
    }

    top10.forEach(st => {
        const item = document.createElement('div');
        item.className = 'station-item';
        item.style.borderLeftColor = getColorForPM25(st.value);
        
        item.innerHTML = `
            <div class="station-info">
                <h4>${st.name}</h4>
                <p>Último reporte: ${st.date}</p>
            </div>
            <div class="station-value ${getTextColorClass(st.value)}">
                ${st.value.toFixed(1)}
            </div>
        `;
        
        // Centrar mapa al hacer click
        item.addEventListener('click', () => {
            if(st.lat && st.lon) {
                map.setView([st.lat, st.lon], 14);
            }
        });
        
        container.appendChild(item);
    });
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadData();
    
    document.getElementById('refreshData').addEventListener('click', loadData);
    
    // API Key Simulator
    document.getElementById('saveApiKey').addEventListener('click', () => {
        const val = document.getElementById('apiKeyInput').value;
        if(val) {
            alert('¡Clave API configurada localmente! (Modo simulado)');
        } else {
            alert('Por favor ingresa una clave API.');
        }
    });
});
