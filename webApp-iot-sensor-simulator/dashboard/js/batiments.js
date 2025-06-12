// Gestion de la section bâtiments

// Variables globales pour les graphiques de bâtiments
let buildingOccupationChart;
let selectedBuilding = null;

/**
 * Initialise la section bâtiments
 */
function initBatimentsSection() {
    // Initialiser le graphique d'occupation
    const buildingOccupationCtx = document.getElementById('building-occupation-chart').getContext('2d');
    buildingOccupationChart = new Chart(buildingOccupationCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Occupation',
                data: [],
                borderColor: CONFIG.CHART.COLORS.PRIMARY,
                backgroundColor: `rgba(52, 152, 219, ${CONFIG.CHART.BACKGROUND_OPACITY})`,
                borderWidth: CONFIG.CHART.BORDER_WIDTH,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sélectionnez un bâtiment'
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
                        text: 'Nombre de personnes'
                    }
                }
            }
        }
    });
}

/**
 * Met à jour les données de la section bâtiments
 */
async function updateBatimentsSection() {
    try {
        // Récupérer les données des bâtiments
        const batimentsData = await fetchAPI('/batiments');
        
        // Mettre à jour les cartes de bâtiments
        updateBuildingsGrid(batimentsData);
        
        // Mettre à jour les détails du bâtiment sélectionné
        if (selectedBuilding) {
            updateBuildingDetails(batimentsData[selectedBuilding]);
            await updateBuildingOccupationChart(selectedBuilding);
        }
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour de la section bâtiments:', error);
    }
}

/**
 * Met à jour la grille des bâtiments
 * @param {Object} batimentsData - Données des bâtiments
 */
function updateBuildingsGrid(batimentsData) {
    const buildingsGrid = document.getElementById('buildings-grid');
    
    // Vider la grille
    buildingsGrid.innerHTML = '';
    
    // Créer une carte pour chaque bâtiment
    Object.entries(batimentsData).forEach(([buildingId, building]) => {
        // Calculer l'occupation totale
        let totalOccupation = 0;
        let totalCapacity = 0;
        
        building.salles.forEach(salle => {
            totalOccupation += salle.occupation_actuelle;
            totalCapacity += salle.capacite;
        });
        
        // Calculer le taux d'occupation
        const occupancyRate = (totalCapacity > 0) ? (totalOccupation / totalCapacity) * 100 : 0;
        const occupancyClass = getOccupancyColorClass(occupancyRate);
        
        // Déterminer le statut du bâtiment
        let statusClass = building.est_ouvert ? 'status-online' : 'status-offline';
        let statusText = building.est_ouvert ? 'Ouvert' : 'Fermé';
        
        const card = document.createElement('div');
        card.className = 'status-card';
        card.innerHTML = `
            <div class="status-card-header">
                <div class="status-card-title">
                    <span class="status-indicator ${statusClass}"></span>
                    <i class="fas fa-building"></i> ${building.nom}
                </div>
            </div>
            <div class="status-card-content">
                <div class="status-detail">
                    <span class="status-label">Statut:</span>
                    <span class="status-value">${statusText}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Heures d'ouverture:</span>
                    <span class="status-value">${building.est_ouvert ? `${building.heure_ouverture} - ${building.heure_fermeture}` : 'Fermé'}</span>
                </div>
                <div class="status-detail">
                    <span class="status-label">Occupation:</span>
                    <span class="status-value">${totalOccupation} / ${totalCapacity}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar ${occupancyClass}" style="width: ${occupancyRate}%"></div>
                </div>
                <div class="status-detail">
                    <span class="status-label">Nombre de salles:</span>
                    <span class="status-value">${building.salles.length}</span>
                </div>
                <button class="view-details-btn" onclick="selectBuilding('${buildingId}')">Voir les détails</button>
            </div>
        `;
        
        buildingsGrid.appendChild(card);
    });
    
    // Ajouter le style pour le bouton de détails
    const style = document.createElement('style');
    style.textContent = `
        .view-details-btn {
            margin-top: 10px;
            padding: 8px 12px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: var(--transition);
        }
        
        .view-details-btn:hover {
            background-color: var(--primary-dark);
        }
    `;
    document.head.appendChild(style);
}

/**
 * Sélectionne un bâtiment pour afficher ses détails
 * @param {string} buildingId - Identifiant du bâtiment
 */
async function selectBuilding(buildingId) {
    selectedBuilding = buildingId;
    
    try {
        // Récupérer les données du bâtiment
        const building = await fetchAPI(`/batiments/${buildingId}`);
        
        // Mettre à jour les détails du bâtiment
        updateBuildingDetails(building);
        
        // Mettre à jour le graphique d'occupation
        await updateBuildingOccupationChart(buildingId);
        
    } catch (error) {
        console.error(`Erreur lors de la sélection du bâtiment ${buildingId}:`, error);
    }
}

/**
 * Met à jour les détails d'un bâtiment
 * @param {Object} building - Données du bâtiment
 */
function updateBuildingDetails(building) {
    const buildingRooms = document.getElementById('building-rooms');
    
    // Vider le conteneur
    buildingRooms.innerHTML = '';
    
    // Ajouter un en-tête
    const header = document.createElement('div');
    header.className = 'building-rooms-header';
    header.innerHTML = `
        <h4>${building.nom}</h4>
        <p>Statut: ${building.est_ouvert ? 'Ouvert' : 'Fermé'}</p>
    `;
    buildingRooms.appendChild(header);
    
    // Ajouter chaque salle
    building.salles.forEach(salle => {
        const occupancyRate = (salle.capacite > 0) ? (salle.occupation_actuelle / salle.capacite) * 100 : 0;
        const occupancyClass = getOccupancyColorClass(occupancyRate);
        
        const roomItem = document.createElement('div');
        roomItem.className = 'room-item';
        roomItem.innerHTML = `
            <div class="room-info">
                <span class="room-name">${salle.nom}</span>
                <span class="room-function">${salle.fonction}</span>
            </div>
            <div class="room-occupancy">
                <span>${salle.occupation_actuelle} / ${salle.capacite}</span>
                <div class="progress-container" style="width: 60px; margin-left: 10px;">
                    <div class="progress-bar ${occupancyClass}" style="width: ${occupancyRate}%"></div>
                </div>
            </div>
        `;
        
        buildingRooms.appendChild(roomItem);
    });
}


/**
 * Met à jour le graphique d'occupation d'un bâtiment
 * @param {string} buildingId - Identifiant du bâtiment
 */
async function updateBuildingOccupationChart(buildingId) {
    try {
        // Récupérer l'historique d'occupation du bâtiment
        const historyData = await fetchAPI(`/batiments/${buildingId}/historique`);
        
        // Récupérer les informations du bâtiment
        const building = await fetchAPI(`/batiments/${buildingId}`);
        
        // Préparer les données pour le graphique
        const dataPoints = historyData.map(point => ({
            x: point.timestamp,
            y: point.occupation_totale
        }));
        
        // Mettre à jour le graphique
        buildingOccupationChart.data.datasets[0].data = dataPoints;
        buildingOccupationChart.options.plugins.title.text = `Occupation - ${building.nom}`;
        buildingOccupationChart.update();
        
    } catch (error) {
        console.error(`Erreur lors de la mise à jour du graphique d'occupation pour le bâtiment ${buildingId}:`, error);
    }
}
