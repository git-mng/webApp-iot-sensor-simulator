// Gestion de la section transport

// Variables globales pour les cartes
let fullTransportMap;
let busMarkers, taxiMarkers;

/**
 * Initialise la section transport
 */
function initTransportSection() {
    // Initialiser la carte des transports
    fullTransportMap = createMap('full-transport-map');
    
    // Créer les groupes de marqueurs
    busMarkers = L.layerGroup().addTo(fullTransportMap);
    taxiMarkers = L.layerGroup().addTo(fullTransportMap);
    
    // Ajouter les contrôles de couches
    const overlays = {
        "Bus": busMarkers,
        "Taxis": taxiMarkers
    };
    
    L.control.layers(null, overlays).addTo(fullTransportMap);
}

/**
 * Met à jour les données de la section transport
 */
async function updateTransportSection() {
    try {
        // Récupérer les données des bus
        const busData = await fetchAPI('/transport/bus');
        
        // Récupérer les données des taxis
        const taxiData = await fetchAPI('/transport/taxi');
        
        // Mettre à jour la carte des transports
        updateTransportMap(busData, taxiData);
        
        // Mettre à jour les listes de bus et taxis
        updateBusList(busData);
        updateTaxiList(taxiData);
        
    } catch (error) {
        console.error('Erreur lors de la mise à jour de la section transport:', error);
    }
}

/**
 * Met à jour la carte des transports
 * @param {Object} busData - Données des bus
 * @param {Object} taxiData - Données des taxis
 */
function updateTransportMap(busData, taxiData) {
    // Effacer les marqueurs existants
    busMarkers.clearLayers();
    taxiMarkers.clearLayers();
    
    // Ajouter les marqueurs des bus
    Object.values(busData).forEach(bus => {
        if (bus.en_service) {
            const busIcon = L.divIcon({
                className: 'bus-marker',
                html: `<i class="fas fa-bus" style="color: ${bus.ligne === 'Ligne1' ? '#3498db' : '#e74c3c'}"></i>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            
            const popupContent = `
                <div class="transport-popup">
                    <h4>${bus.nom_ligne}</h4>
                    <p><strong>De:</strong> ${bus.arret_actuel}</p>
                    <p><strong>Vers:</strong> ${bus.arret_suivant}</p>
                    <p><strong>Passagers:</strong> ${bus.passagers}/${bus.capacite}</p>
                    <p><strong>Retard:</strong> ${bus.retard} min</p>
                </div>
            `;
            
            L.marker([bus.latitude, bus.longitude], { icon: busIcon })
                .bindPopup(popupContent)
                .addTo(busMarkers);
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
            
            const popupContent = `
                <div class="transport-popup">
                    <h4>Taxi ${taxi.id}</h4>
                    <p><strong>Zone:</strong> ${taxi.nom_zone}</p>
                    <p><strong>Statut:</strong> ${taxi.disponible ? 'Disponible' : 'Occupé'}</p>
                    <p><strong>Vitesse:</strong> ${taxi.vitesse} km/h</p>
                </div>
            `;
            
            L.marker([taxi.latitude, taxi.longitude], { icon: taxiIcon })
                .bindPopup(popupContent)
                .addTo(taxiMarkers);
        }
    });
    
    // Ajouter le style pour les popups
    const style = document.createElement('style');
    style.textContent = `
        .transport-popup {
            padding: 5px;
        }
        
        .transport-popup h4 {
            margin: 0 0 8px 0;
            font-size: 14px;
        }
        
        .transport-popup p {
            margin: 5px 0;
            font-size: 12px;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Met à jour la liste des bus
 * @param {Object} busData - Données des bus
 */
function updateBusList(busData) {
    const busList = document.getElementById('bus-list');
    
    // Vider la liste
    busList.innerHTML = '';
    
    // Trier les bus par ligne
    const sortedBuses = Object.values(busData).sort((a, b) => {
        if (a.ligne !== b.ligne) {
            return a.ligne.localeCompare(b.ligne);
        }
        return a.id.localeCompare(b.id);
    });
    
    // Créer un élément pour chaque bus
    sortedBuses.forEach(bus => {
        // Déterminer le statut du bus
        let statusClass = bus.en_service ? 'status-available' : 'status-busy';
        let statusText = bus.en_service ? 'En service' : 'Hors service';
        
        // Calculer le taux d'occupation
        const occupancyRate = (bus.capacite > 0) ? (bus.passagers / bus.capacite) * 100 : 0;
        
        const busItem = document.createElement('div');
        busItem.className = 'transport-item';
        busItem.innerHTML = `
            <div class="transport-item-info">
                <span class="transport-item-title">${bus.nom_ligne} (${bus.id})</span>
                <span class="transport-item-subtitle">
                    ${bus.en_service ? `De: ${bus.arret_actuel} → Vers: ${bus.arret_suivant}` : 'Inactif'}
                </span>
            </div>
            <div class="transport-item-status">
                <div class="status-badge ${statusClass}">${statusText}</div>
                ${bus.en_service ? `
                <div class="transport-occupancy">
                    <span>${bus.passagers}/${bus.capacite}</span>
                    <div class="progress-container" style="width: 60px; margin-left: 10px;">
                        <div class="progress-bar ${getOccupancyColorClass(occupancyRate)}" style="width: ${occupancyRate}%"></div>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        busList.appendChild(busItem);
    });
}

/**
 * Met à jour la liste des taxis
 * @param {Object} taxiData - Données des taxis
 */
function updateTaxiList(taxiData) {
    const taxiList = document.getElementById('taxi-list');
    
    // Vider la liste
    taxiList.innerHTML = '';
    
    // Trier les taxis par zone
    const sortedTaxis = Object.values(taxiData).sort((a, b) => {
        if (a.zone !== b.zone) {
            return a.zone.localeCompare(b.zone);
        }
        return a.id.localeCompare(b.id);
    });
    
    // Créer un élément pour chaque taxi
    sortedTaxis.forEach(taxi => {
        // Déterminer le statut du taxi
        let statusClass = taxi.disponible ? 'status-available' : 'status-busy';
        let statusText = taxi.disponible ? 'Disponible' : 'Occupé';
        
        // Déterminer le statut de mouvement
        let movementText = taxi.en_mouvement ? 'En mouvement' : 'À l\'arrêt';
        
        const taxiItem = document.createElement('div');
        taxiItem.className = 'transport-item';
        taxiItem.innerHTML = `
            <div class="transport-item-info">
                <span class="transport-item-title">Taxi ${taxi.id}</span>
                <span class="transport-item-subtitle">
                    Zone: ${taxi.nom_zone} - ${movementText}
                </span>
            </div>
            <div class="transport-item-status">
                <div class="status-badge ${statusClass}">${statusText}</div>
                ${taxi.en_mouvement ? `
                <div class="taxi-speed">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>${taxi.vitesse} km/h</span>
                </div>
                ` : ''}
            </div>
        `;
        
        taxiList.appendChild(taxiItem);
    });
}
