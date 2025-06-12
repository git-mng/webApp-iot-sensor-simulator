// Gestion de la section parking

// Variables globales pour les graphiques de parking
let parkingHistoryChart;

/**
 * Initialise la section parking
 */
function initParkingSection() {
    // Initialiser le graphique d'historique
    const parkingHistoryCtx = document.getElementById('parking-history-chart').getContext('2d');
    parkingHistoryChart = new Chart(parkingHistoryCtx, {
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
                    title: {
                        display: true,
                        text: 'Places disponibles'
                    }
                }
            }
        }
    });
}

/**
 * Met à jour les données de la section parking
 */
async function updateParkingSection() {
    try {
        // Récupérer les données des parkings
        const parkingData = await fetchAPI('/parking');
        
        // Mettre à jour les cartes de statut
        updateParkingStatusCards(parkingData);
        
        // Mettre à jour le graphique d'historique
        updateParkingHistoryChart(parkingData);
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour de la section parking:', error);
    }
}

/**
 * Met à jour les cartes de statut des parkings
 * @param {Object} parkingData - Données des parkings
 */
function updateParkingStatusCards(parkingData) {
    const parkingStatusContainer = document.getElementById('parking-status');
    
    // Vider le conteneur
    parkingStatusContainer.innerHTML = '';
    
    // Créer une carte pour chaque parking
    Object.values(parkingData).forEach(parking => {
        // Calculer le taux d'occupation
        const occupancyRate = ((parking.capacite_totale - parking.places_disponibles) / parking.capacite_totale) * 100;
        const occupancyClass = getOccupancyColorClass(occupancyRate);
        
        const card = document.createElement('div');
        card.className = 'status-card';
        card.innerHTML = `
            <div class="status-card-header">
                <div class="status-card-title">
                    <i class="fas fa-parking"></i> ${parking.nom}
                </div>
            </div>
            <div class="status-card-content">
                <div class="status-detail">
                    <span class="status-label">Places disponibles:</span>
                    <span class="status-value">${parking.places_disponibles} / ${parking.capacite_totale}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Taux d'occupation:</span>
                    <span class="status-value">${Math.round(occupancyRate)}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar ${occupancyClass}" style="width: ${occupancyRate}%"></div>
                </div>
                <div class="status-detail">
                    <span class="status-label">Dernière mise à jour:</span>
                    <span class="status-value">${formatTime(parking.timestamp)}</span>
                </div>
            </div>
        `;
        
        parkingStatusContainer.appendChild(card);
    });
}

/**
 * Met à jour le graphique d'historique des parkings
 * @param {Object} parkingData - Données des parkings
 */
async function updateParkingHistoryChart(parkingData) {
    try {
        // Préparer les datasets pour le graphique
        const datasets = [];
        const colors = [
            CONFIG.CHART.COLORS.PRIMARY,
            CONFIG.CHART.COLORS.SECONDARY,
            CONFIG.CHART.COLORS.ACCENT,
            CONFIG.CHART.COLORS.INFO,
            CONFIG.CHART.COLORS.WARNING
        ];
        
        // Pour chaque parking, récupérer l'historique
        let i = 0;
        for (const parkingId of Object.keys(parkingData)) {
            const historyData = await fetchAPI(`/parking/${parkingId}/historique`);
            
            // Préparer les données pour le graphique
            const dataPoints = historyData.map(point => ({
                x: point.timestamp,
                y: point.places_disponibles
            }));
            
            // Ajouter le dataset
            datasets.push({
                label: parkingData[parkingId].nom,
                data: dataPoints,
                borderColor: colors[i % colors.length],
                backgroundColor: `rgba(${hexToRgb(colors[i % colors.length])}, ${CONFIG.CHART.BACKGROUND_OPACITY})`,
                borderWidth: CONFIG.CHART.BORDER_WIDTH,
                tension: 0.4,
                fill: false
            });
            
            i++;
        }
        
        // Mettre à jour le graphique
        parkingHistoryChart.data.datasets = datasets;
        parkingHistoryChart.update();
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour du graphique d\'historique des parkings:', error);
    }
}

/**
 * Convertit une couleur hexadécimale en RGB
 * @param {string} hex - Couleur hexadécimale
 * @returns {string} Couleur au format RGB
 */
function hexToRgb(hex) {
    // Supprimer le # si présent
    hex = hex.replace('#', '');
    
    // Convertir en RGB
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    
    return `${r}, ${g}, ${b}`;
}
