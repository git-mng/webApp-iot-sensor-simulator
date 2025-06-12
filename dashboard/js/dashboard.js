// Gestion du tableau de bord principal

// Variables globales pour les graphiques de la dashboard
let parkingChart, buildingsChart, wifiChart;

/**
 * Initialise les graphiques du tableau de bord principal
 */
function initDashboardCharts() {
    // Graphique de disponibilité des parkings
    const parkingCtx = document.getElementById('parking-chart').getContext('2d');
    parkingChart = new Chart(parkingCtx, {
        type: 'doughnut',
        data: {
            labels: ['Disponibles', 'Occupés'],
            datasets: [{
                data: [0, 0],
                backgroundColor: [
                    CONFIG.CHART.COLORS.SUCCESS,
                    CONFIG.CHART.COLORS.NEUTRAL
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            cutout: '70%',
            animation: {
                duration: CONFIG.CHART.ANIMATION_DURATION
            }
        }
    });
    
    // Graphique d'occupation des bâtiments
    const buildingsCtx = document.getElementById('buildings-chart').getContext('2d');
    buildingsChart = new Chart(buildingsCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Occupation',
                data: [],
                backgroundColor: CONFIG.CHART.COLORS.PRIMARY,
                borderWidth: 0,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            },
            animation: {
                duration: CONFIG.CHART.ANIMATION_DURATION
            }
        }
    });
    
    // Graphique d'utilisateurs WiFi
    const wifiCtx = document.getElementById('wifi-chart').getContext('2d');
    wifiChart = new Chart(wifiCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Utilisateurs',
                data: [],
                borderColor: CONFIG.CHART.COLORS.INFO,
                backgroundColor: `rgba(52, 152, 219, ${CONFIG.CHART.BACKGROUND_OPACITY})`,
                borderWidth: CONFIG.CHART.BORDER_WIDTH,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            },
            animation: {
                duration: CONFIG.CHART.ANIMATION_DURATION
            }
        }
    });
}

/**
 * Met à jour les métriques du tableau de bord
 */
async function updateDashboardMetrics() {
    try {
        // Récupérer les données des parkings
        const parkingData = await fetchAPI('/parking');
        updateParkingMetrics(parkingData);
        
        // Récupérer les données des bâtiments
        const batimentsData = await fetchAPI('/batiments');
        updateBuildingsMetrics(batimentsData);
        
        // Récupérer les données WiFi
        const wifiData = await fetchAPI('/wifi');
        updateWifiMetrics(wifiData);
        
        // Récupérer les données météo
        const meteoData = await fetchAPI('/meteo');
        updateWeatherMetrics(meteoData);
        
        // Récupérer les données de transport
        const busData = await fetchAPI('/transport/bus');
        const taxiData = await fetchAPI('/transport/taxi');
        updateTransportMetrics(busData, taxiData);
        
        // Mettre à jour l'heure de dernière mise à jour
        updateLastUpdateTime();
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour des métriques du tableau de bord:', error);
    }
}

/**
 * Met à jour les métriques de parking
 * @param {Object} parkingData - Données des parkings
 */
function updateParkingMetrics(parkingData) {
    // Calculer le nombre total de places disponibles
    let totalAvailable = 0;
    let totalCapacity = 0;
    
    Object.values(parkingData).forEach(parking => {
        totalAvailable += parking.places_disponibles;
        totalCapacity += parking.capacite_totale;
    });
    
    // Mettre à jour l'affichage du nombre total de places disponibles
    document.getElementById('parking-total').textContent = totalAvailable;
    
    // Mettre à jour le graphique
    if (parkingChart) {
        parkingChart.data.datasets[0].data = [totalAvailable, totalCapacity - totalAvailable];
        parkingChart.update();
    }
}

/**
 * Met à jour les métriques des bâtiments
 * @param {Object} batimentsData - Données des bâtiments
 */
function updateBuildingsMetrics(batimentsData) {
    // Compter les bâtiments ouverts
    const openBuildings = Object.values(batimentsData).filter(batiment => batiment.est_ouvert).length;
    document.getElementById('buildings-open').textContent = openBuildings;
    
    // Préparer les données pour le graphique
    const buildingNames = [];
    const occupationData = [];
    
    Object.values(batimentsData).forEach(batiment => {
        buildingNames.push(batiment.nom.split(' ')[1]); // Simplifier le nom
        
        // Calculer l'occupation totale
        let totalOccupation = 0;
        batiment.salles.forEach(salle => {
            totalOccupation += salle.occupation_actuelle;
        });
        
        occupationData.push(totalOccupation);
    });
    
    // Mettre à jour le graphique
    if (buildingsChart) {
        buildingsChart.data.labels = buildingNames;
        buildingsChart.data.datasets[0].data = occupationData;
        buildingsChart.update();
    }
}

/**
 * Met à jour les métriques WiFi
 * @param {Object} wifiData - Données WiFi
 */
function updateWifiMetrics(wifiData) {
    // Calculer le nombre total d'utilisateurs connectés
    let totalUsers = 0;
    
    Object.values(wifiData).forEach(point => {
        if (point.est_en_ligne) {
            totalUsers += point.utilisateurs_connectes;
        }
    });
    
    // Mettre à jour l'affichage du nombre total d'utilisateurs
    document.getElementById('wifi-users').textContent = totalUsers;
    
    // Préparer les données pour le graphique
    // On utilise les 5 dernières minutes (simulation)
    const timeLabels = [];
    const userData = [];
    
    for (let i = 5; i >= 0; i--) {
        timeLabels.push(moment().subtract(i, 'minutes').format('HH:mm'));
        // Simuler une légère variation
        const variation = Math.floor(Math.random() * 10) - 5;
        userData.push(Math.max(0, totalUsers + variation));
    }
    
    // Mettre à jour le graphique
    if (wifiChart) {
        wifiChart.data.labels = timeLabels;
        wifiChart.data.datasets[0].data = userData;
        wifiChart.update();
    }
}

/**
 * Met à jour les métriques météo
 * @param {Object} meteoData - Données météo
 */
function updateWeatherMetrics(meteoData) {
    // Prendre la première station météo disponible
    const station = Object.values(meteoData)[0];
    
    if (station) {
        // Mettre à jour l'affichage de la température
        document.getElementById('weather-temp').textContent = `${station.temperature}°C`;
        
        // Mettre à jour l'affichage de la description
        document.getElementById('weather-desc').textContent = station.etat_ciel;
        
        // Mettre à jour l'affichage de l'humidité
        document.getElementById('weather-humidity').textContent = `${station.humidite}%`;
        
        // Mettre à jour l'icône
        const iconClass = getWeatherIcon(station.etat_ciel);
        document.getElementById('weather-icon').className = `fas ${iconClass}`;
    }
}

/**
 * Met à jour les métriques de transport
 * @param {Object} busData - Données des bus
 * @param {Object} taxiData - Données des taxis
 */
function updateTransportMetrics(busData, taxiData) {
    // Compter les bus en service
    const activeBuses = Object.values(busData).filter(bus => bus.en_service).length;
    document.getElementById('bus-count').textContent = activeBuses;
    
    // Compter les taxis disponibles
    const availableTaxis = Object.values(taxiData).filter(taxi => taxi.disponible).length;
    document.getElementById('taxi-count').textContent = availableTaxis;
    
    // Initialiser la carte des transports si elle n'existe pas déjà
    if (!window.transportMap) {
        window.transportMap = createMap('transport-map');
        window.transportBusMarkers = L.layerGroup().addTo(window.transportMap);
        window.transportTaxiMarkers = L.layerGroup().addTo(window.transportMap);
    } else {
        // Effacer les marqueurs existants
        window.transportBusMarkers.clearLayers();
        window.transportTaxiMarkers.clearLayers();
    }
    
    // Ajouter les marqueurs des bus
    Object.values(busData).forEach(bus => {
        if (bus.en_service) {
            const busIcon = L.divIcon({
                className: 'bus-marker',
                html: `<i class="fas fa-bus" style="color: ${bus.ligne === 'Ligne1' ? '#3498db' : '#e74c3c'}"></i>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            
            L.marker([bus.latitude, bus.longitude], { icon: busIcon })
                .bindPopup(`<b>${bus.nom_ligne}</b><br>De: ${bus.arret_actuel}<br>Vers: ${bus.arret_suivant}`)
                .addTo(window.transportBusMarkers);
        }
    });
    
    // Ajouter les marqueurs des taxis
    Object.values(taxiData).forEach(taxi => {
        if (taxi.en_mouvement) {
            const taxiIcon = L.divIcon({
                className: 'taxi-marker',
                html: `<i class="fas fa-taxi" style="color: ${taxi.disponible ? '#2ecc71' : '#f39c12'}"></i>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            
            L.marker([taxi.latitude, taxi.longitude], { icon: taxiIcon })
                .bindPopup(`<b>Taxi ${taxi.id}</b><br>Zone: ${taxi.nom_zone}<br>Statut: ${taxi.disponible ? 'Disponible' : 'Occupé'}`)
                .addTo(window.transportTaxiMarkers);
        }
    });
}
