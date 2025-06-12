// Gestion de la section WiFi

// Variables globales pour les graphiques WiFi
let wifiUsersChart, wifiSignalChart;

/**
 * Initialise la section WiFi
 */
function initWifiSection() {
    // Initialiser le graphique d'utilisateurs WiFi
    const wifiUsersCtx = document.getElementById('wifi-users-chart').getContext('2d');
    wifiUsersChart = new Chart(wifiUsersCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Utilisateurs connectés',
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
                    title: {
                        display: true,
                        text: 'Nombre d\'utilisateurs'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Point d\'accès'
                    }
                }
            }
        }
    });
    
    // Initialiser le graphique de puissance du signal
    const wifiSignalCtx = document.getElementById('wifi-signal-chart').getContext('2d');
    wifiSignalChart = new Chart(wifiSignalCtx, {
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
                        text: 'Puissance du signal (%)'
                    },
                    max: 100
                }
            }
        }
    });
}

/**
 * Met à jour les données de la section WiFi
 */
async function updateWifiSection() {
    try {
        // Récupérer les données WiFi
        const wifiData = await fetchAPI('/wifi');
        
        // Mettre à jour les cartes de statut WiFi
        updateWifiStatusGrid(wifiData);
        
        // Mettre à jour les graphiques
        updateWifiCharts(wifiData);
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour de la section WiFi:', error);
    }
}

/**
 * Met à jour la grille de statut WiFi
 * @param {Object} wifiData - Données WiFi
 */
function updateWifiStatusGrid(wifiData) {
    const wifiStatusGrid = document.getElementById('wifi-status-grid');
    
    // Vider la grille
    wifiStatusGrid.innerHTML = '';
    
    // Créer une carte pour chaque point d'accès
    Object.values(wifiData).forEach(point => {
        // Déterminer le statut du point d'accès
        let statusClass = point.est_en_ligne ? 'status-online' : 'status-offline';
        let statusText = point.est_en_ligne ? 'En ligne' : 'Hors ligne';
        
        // Déterminer la classe pour le niveau de congestion
        let congestionClass = 'progress-low';
        if (point.niveau_congestion > 50) {
            congestionClass = 'progress-medium';
        } else if (point.niveau_congestion > 80) {
            congestionClass = 'progress-high';
        }
        
        const card = document.createElement('div');
        card.className = 'status-card';
        card.innerHTML = `
            <div class="status-card-header">
                <div class="status-card-title">
                    <span class="status-indicator ${statusClass}"></span>
                    <i class="fas fa-wifi"></i> ${point.nom}
                </div>
            </div>
            <div class="status-card-content">
                <div class="status-detail">
                    <span class="status-label">Statut:</span>
                    <span class="status-value">${statusText}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Localisation:</span>
                    <span class="status-value">${point.localisation}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Puissance du signal:</span>
                    <span class="status-value">${point.est_en_ligne ? `${point.puissance_signal}%` : 'N/A'}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Utilisateurs connectés:</span>
                    <span class="status-value">${point.est_en_ligne ? point.utilisateurs_connectes : 'N/A'}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Bande passante utilisée:</span>
                    <span class="status-value">${point.est_en_ligne ? `${point.bande_passante_utilisee} Mbps` : 'N/A'}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Niveau de congestion:</span>
                    <span class="status-value">${point.est_en_ligne ? `${point.niveau_congestion}%` : 'N/A'}</span>
                </div>
                ${point.est_en_ligne ? `
                <div class="progress-container">
                    <div class="progress-bar ${congestionClass}" style="width: ${point.niveau_congestion}%"></div>
                </div>
                ` : ''}
                <div class="status-detail">
                    <span class="status-label">Dernière mise à jour:</span>
                    <span class="status-value">${formatTime(point.timestamp)}</span>
                </div>
            </div>
        `;
        
        wifiStatusGrid.appendChild(card);
    });
}

/**
 * Met à jour les graphiques WiFi
 * @param {Object} wifiData - Données WiFi
 */
async function updateWifiCharts(wifiData) {
    try {
        // Préparer les données pour le graphique d'utilisateurs
        const apNames = [];
        const usersData = [];
        
        Object.values(wifiData).forEach(point => {
            if (point.est_en_ligne) {
                // Simplifier le nom pour l'affichage
                const shortName = point.nom.replace('WiFi-', '').replace('-', ' ');
                apNames.push(shortName);
                usersData.push(point.utilisateurs_connectes);
            }
        });
        
        // Mettre à jour le graphique d'utilisateurs
        wifiUsersChart.data.labels = apNames;
        wifiUsersChart.data.datasets[0].data = usersData;
        wifiUsersChart.update();
        
        // Préparer les données pour le graphique de puissance du signal
        const datasets = [];
        const colors = [
            CONFIG.CHART.COLORS.PRIMARY,
            CONFIG.CHART.COLORS.SECONDARY,
            CONFIG.CHART.COLORS.ACCENT,
            CONFIG.CHART.COLORS.INFO,
            CONFIG.CHART.COLORS.WARNING
        ];
        
        // Pour chaque point d'accès, récupérer l'historique
        let i = 0;
        for (const wifiId of Object.keys(wifiData)) {
            if (wifiData[wifiId].est_en_ligne) {
                const historyData = await fetchAPI(`/wifi/${wifiId}/historique`);
                
                // Préparer les données pour le graphique
                const dataPoints = historyData.map(point => ({
                    x: point.timestamp,
                    y: point.puissance_signal
                }));
                
                // Simplifier le nom pour l'affichage
                const shortName = wifiData[wifiId].nom.replace('WiFi-', '').replace('-', ' ');
                
                // Ajouter le dataset
                datasets.push({
                    label: shortName,
                    data: dataPoints,
                    borderColor: colors[i % colors.length],
                    backgroundColor: `rgba(${hexToRgb(colors[i % colors.length])}, ${CONFIG.CHART.BACKGROUND_OPACITY})`,
                    borderWidth: CONFIG.CHART.BORDER_WIDTH,
                    tension: 0.4,
                    fill: false
                });
                
                i++;
            }
        }
        
        // Mettre à jour le graphique de puissance du signal
        wifiSignalChart.data.datasets = datasets;
        wifiSignalChart.update();
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour des graphiques WiFi:', error);
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
