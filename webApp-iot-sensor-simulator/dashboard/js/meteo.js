// Gestion de la section météo

// Variables globales pour les graphiques météo
let temperatureChart, humidityChart;

/**
 * Initialise la section météo
 */
function initMeteoSection() {
    // Initialiser le graphique de température
    const temperatureCtx = document.getElementById('temperature-chart').getContext('2d');
    temperatureChart = new Chart(temperatureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            return moment.unix(tooltipItems[0].parsed.x).format('HH:mm:ss');
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        },
                        tooltipFormat: 'HH:mm:ss'
                    },
                    title: {
                        display: true,
                        text: 'Heure'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Température (°C)'
                    }
                }
            }
        }
    });
    
    // Initialiser le graphique d'humidité
    const humidityCtx = document.getElementById('humidity-chart').getContext('2d');
    humidityChart = new Chart(humidityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            return moment.unix(tooltipItems[0].parsed.x).format('HH:mm:ss');
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        },
                        tooltipFormat: 'HH:mm:ss'
                    },
                    title: {
                        display: true,
                        text: 'Heure'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Humidité (%)'
                    }
                }
            }
        }
    });
}

/**
 * Met à jour les données de la section météo
 */
async function updateMeteoSection() {
    try {
        // Récupérer les données météo
        const meteoData = await fetchAPI('/meteo');
        
        // Mettre à jour les cartes des stations météo
        updateWeatherStationsGrid(meteoData);
        
        // Mettre à jour les graphiques
        updateWeatherCharts(meteoData);
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour de la section météo:', error);
    }
}

/**
 * Met à jour la grille des stations météo
 * @param {Object} meteoData - Données météo
 */
function updateWeatherStationsGrid(meteoData) {
    const weatherStationsGrid = document.getElementById('weather-stations-grid');
    
    // Vider la grille
    weatherStationsGrid.innerHTML = '';
    
    // Créer une carte pour chaque station météo
    Object.values(meteoData).forEach(station => {
        // Obtenir l'icône pour l'état du ciel
        const weatherIconClass = getWeatherIcon(station.etat_ciel);
        
        const card = document.createElement('div');
        card.className = 'status-card';
        card.innerHTML = `
            <div class="status-card-header">
                <div class="status-card-title">
                    <i class="fas fa-cloud-sun"></i> ${station.nom}
                </div>
            </div>
            <div class="status-card-content">
                <div class="weather-overview">
                    <div class="weather-icon">
                        <i class="fas ${weatherIconClass}"></i>
                    </div>
                    <div class="weather-details">
                        <div class="weather-temp">
                            <span class="temp-value">${station.temperature}°C</span>
                        </div>
                        <div class="weather-desc">
                            <span>${station.etat_ciel}</span>
                        </div>
                        <div class="weather-humidity">
                            <i class="fas fa-tint"></i>
                            <span>${station.humidite}%</span>
                        </div>
                    </div>
                </div>
                <div class="weather-additional-info">
                    <div class="status-detail">
                        <span class="status-label">Pression:</span>
                        <span class="status-value">${station.pression} hPa</span>
                    </div>
                    <div class="status-detail">
                        <span class="status-label">Vent:</span>
                        <span class="status-value">${station.vitesse_vent} km/h, ${station.direction_vent}°</span>
                    </div>
                    <div class="status-detail">
                        <span class="status-label">Précipitations:</span>
                        <span class="status-value">${station.precipitations} mm</span>
                    </div>
                    <div class="status-detail">
                        <span class="status-label">Dernière mise à jour:</span>
                        <span class="status-value">${formatTime(station.timestamp)}</span>
                    </div>
                </div>
            </div>
        `;
        
        weatherStationsGrid.appendChild(card);
    });
    
    // Ajouter le style pour les informations supplémentaires
    const style = document.createElement('style');
    style.textContent = `
        .weather-additional-info {
            margin-top: 15px;
            border-top: 1px solid var(--border-color);
            padding-top: 15px;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Met à jour les graphiques météo
 * @param {Object} meteoData - Données météo
 */
async function updateWeatherCharts(meteoData) {
    try {
        const colors = [
            CONFIG.CHART.COLORS.PRIMARY,
            CONFIG.CHART.COLORS.SECONDARY,
            CONFIG.CHART.COLORS.ACCENT,
            CONFIG.CHART.COLORS.INFO,
            CONFIG.CHART.COLORS.WARNING
        ];
        
        // Datasets pour la température
        const temperatureDatasets = [];
        
        // Datasets pour l'humidité
        const humidityDatasets = [];
        
        // Pour chaque station météo, récupérer l'historique
        let i = 0;
        for (const stationId of Object.keys(meteoData)) {
            const historyData = await fetchAPI(`/meteo/${stationId}/historique`);
            
            // Préparer les données pour le graphique de température
            const temperaturePoints = historyData.map(point => ({
                x: point.timestamp,
                y: point.temperature
            }));
            
            // Préparer les données pour le graphique d'humidité
            const humidityPoints = historyData.map(point => ({
                x: point.timestamp,
                y: point.humidite
            }));
            
            // Ajouter le dataset de température
            temperatureDatasets.push({
                label: meteoData[stationId].nom,
                data: temperaturePoints,
                borderColor: colors[i % colors.length],
                backgroundColor: `rgba(${hexToRgb(colors[i % colors.length])}, ${CONFIG.CHART.BACKGROUND_OPACITY})`,
                borderWidth: CONFIG.CHART.BORDER_WIDTH,
                tension: 0.4,
                fill: false
            });
            
            // Ajouter le dataset d'humidité
            humidityDatasets.push({
                label: meteoData[stationId].nom,
                data: humidityPoints,
                borderColor: colors[i % colors.length],
                backgroundColor: `rgba(${hexToRgb(colors[i % colors.length])}, ${CONFIG.CHART.BACKGROUND_OPACITY})`,
                borderWidth: CONFIG.CHART.BORDER_WIDTH,
                tension: 0.4,
                fill: false
            });
            
            i++;
        }
        
        // Mettre à jour le graphique de température
        temperatureChart.data.datasets = temperatureDatasets;
        temperatureChart.update();
        
        // Mettre à jour le graphique d'humidité
        humidityChart.data.datasets = humidityDatasets;
        humidityChart.update();
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour des graphiques météo:', error);
    }
}
