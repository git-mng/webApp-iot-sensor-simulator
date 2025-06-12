#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulateur de capteurs pour le suivi des transports publics.
Ce script génère des données de position GPS simulées pour les bus et taxis
et les publie sur un topic MQTT.
"""

import json
import random
import time
import uuid
import math
from datetime import datetime
from paho.mqtt import client as mqtt_client
import sys
import os

# Tentative d'importation de geopy, avec fallback si non disponible
try:
    from geopy.distance import geodesic
    GEOPY_DISPONIBLE = True
except ImportError:
    GEOPY_DISPONIBLE = False
    print("Warning: geopy non disponible, calcul de distance simplifié sera utilisé")

# Ajout du répertoire parent au path pour importer config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BROKER_ADRESSE, BROKER_PORT, CLIENT_ID_BASE, TOPIC_TRANSPORT, INTERVALLE_TRANSPORT

# Définition des lignes de bus (points de passage avec coordonnées GPS)
LIGNES_BUS = {
    "Ligne1": {
        "nom": "Ligne 1 - Campus Express",
        "arrets": [
            {"nom": "Gare Centrale", "latitude": 48.8566, "longitude": 2.3522},
            {"nom": "Faculté des Sciences", "latitude": 48.8570, "longitude": 2.3530},
            {"nom": "Bibliothèque Universitaire", "latitude": 48.8575, "longitude": 2.3535},
            {"nom": "Résidence Étudiante", "latitude": 48.8580, "longitude": 2.3540},
            {"nom": "Centre Sportif", "latitude": 48.8585, "longitude": 2.3545},
            {"nom": "Restaurant Universitaire", "latitude": 48.8590, "longitude": 2.3550}
        ],
        "frequence_passage": 10,  # en minutes
        "vitesse_moyenne": 20     # en km/h
    },
    "Ligne2": {
        "nom": "Ligne 2 - Navette Ville",
        "arrets": [
            {"nom": "Mairie", "latitude": 48.8600, "longitude": 2.3400},
            {"nom": "Centre Commercial", "latitude": 48.8605, "longitude": 2.3405},
            {"nom": "Parc Municipal", "latitude": 48.8610, "longitude": 2.3410},
            {"nom": "Faculté des Lettres", "latitude": 48.8615, "longitude": 2.3415},
            {"nom": "Hôpital", "latitude": 48.8620, "longitude": 2.3420}
        ],
        "frequence_passage": 15,  # en minutes
        "vitesse_moyenne": 18     # en km/h
    }
}

# Zones de circulation des taxis (centre et rayon en km)
ZONES_TAXIS = {
    "ZoneCampus": {
        "nom": "Zone Campus",
        "centre": {"latitude": 48.8580, "longitude": 2.3540},
        "rayon": 2.0  # rayon en km
    },
    "ZoneCentre": {
        "nom": "Zone Centre-Ville",
        "centre": {"latitude": 48.8610, "longitude": 2.3410},
        "rayon": 1.5  # rayon en km
    }
}

# Créer les véhicules (bus et taxis)
BUS = []
for ligne_id, ligne in LIGNES_BUS.items():
    # Créer plusieurs bus par ligne
    nombre_bus = max(1, int(60 / ligne["frequence_passage"]))  # Au moins 1 bus
    for i in range(nombre_bus):
        # Répartir les bus le long de la ligne
        position_initiale = i % len(ligne["arrets"])
        position_suivante = (position_initiale + 1) % len(ligne["arrets"])
        progression = random.random()  # Progression entre les deux arrêts
        
        BUS.append({
            "id": f"BUS_{ligne_id}_{i+1}",
            "ligne": ligne_id,
            "nom_ligne": ligne["nom"],
            "position_arret_actuel": position_initiale,
            "position_arret_suivant": position_suivante,
            "progression": progression,
            "vitesse": ligne["vitesse_moyenne"] * (0.8 + random.random() * 0.4),  # Variation de vitesse
            "en_service": random.random() < 0.9,  # 90% des bus en service
            "capacite": 50,
            "passagers": random.randint(0, 40)
        })

TAXIS = []
for zone_id, zone in ZONES_TAXIS.items():
    # Créer plusieurs taxis par zone
    nombre_taxis = random.randint(3, 8)
    for i in range(nombre_taxis):
        # Position aléatoire dans la zone
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, zone["rayon"])
        
        # Calcul des coordonnées (approximation simple)
        lat_km = 111.32  # km par degré de latitude (approximation)
        lon_km = 111.32 * math.cos(math.radians(zone["centre"]["latitude"]))  # km par degré de longitude
        
        latitude = zone["centre"]["latitude"] + (distance * math.sin(angle)) / lat_km
        longitude = zone["centre"]["longitude"] + (distance * math.cos(angle)) / lon_km
        
        TAXIS.append({
            "id": f"TAXI_{zone_id}_{i+1}",
            "zone": zone_id,
            "nom_zone": zone["nom"],
            "latitude": latitude,
            "longitude": longitude,
            "vitesse": random.uniform(0, 50),  # Vitesse en km/h
            "disponible": random.random() < 0.7,  # 70% des taxis disponibles
            "en_mouvement": random.random() < 0.6,  # 60% des taxis en mouvement
            "destination": {
                "latitude": zone["centre"]["latitude"] + random.uniform(-0.01, 0.01),
                "longitude": zone["centre"]["longitude"] + random.uniform(-0.01, 0.01)
            } if random.random() < 0.6 else None  # 60% avec une destination
        })

def connecter_mqtt():
    """Établit une connexion au broker MQTT."""
    # Génération d'un ID client unique
    id_client = f"{CLIENT_ID_BASE}transport_{str(uuid.uuid4())[:8]}"
    
    def au_connexion(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connecté au broker MQTT! ID client: {id_client}")
        else:
            print(f"Échec de connexion, code retour {rc}")
    
    # Création du client MQTT
    client = mqtt_client.Client(client_id=id_client, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1)
    client.on_connect = au_connexion
    client.connect(BROKER_ADRESSE, BROKER_PORT)
    return client

def calculer_distance_gps(point1, point2):
    """Calcule la distance entre deux points GPS en kilomètres."""
    if GEOPY_DISPONIBLE:
        return geodesic((point1["latitude"], point1["longitude"]), 
                         (point2["latitude"], point2["longitude"])).kilometers
    else:
        # Calcul simplifié de la distance (formule de Haversine)
        lat1, lon1 = math.radians(point1["latitude"]), math.radians(point1["longitude"])
        lat2, lon2 = math.radians(point2["latitude"]), math.radians(point2["longitude"])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Rayon de la Terre en kilomètres
        
        return c * r

def interpoler_position(point1, point2, progression):
    """Interpoler entre deux points GPS selon une progression (0-1)."""
    return {
        "latitude": point1["latitude"] + progression * (point2["latitude"] - point1["latitude"]),
        "longitude": point1["longitude"] + progression * (point2["longitude"] - point1["longitude"])
    }

def mettre_a_jour_position_bus(bus, delta_temps):
    """Met à jour la position d'un bus selon sa vitesse et le temps écoulé."""
    # Si le bus n'est pas en service, ne pas modifier sa position
    if not bus["en_service"]:
        return
    
    ligne = LIGNES_BUS[bus["ligne"]]
    arrets = ligne["arrets"]
    
    # Calculer la distance entre les arrêts actuel et suivant
    arret_actuel = arrets[bus["position_arret_actuel"]]
    arret_suivant = arrets[bus["position_arret_suivant"]]
    distance_totale = calculer_distance_gps(arret_actuel, arret_suivant)
    
    # Calculer la progression supplémentaire basée sur la vitesse et le temps
    vitesse_km_s = bus["vitesse"] / 3600  # Convertir km/h en km/s
    distance_parcourue = vitesse_km_s * delta_temps  # Distance parcourue en km
    progression_supplementaire = distance_parcourue / distance_totale
    
    # Mettre à jour la progression
    bus["progression"] += progression_supplementaire
    
    # Si le bus a dépassé l'arrêt suivant
    if bus["progression"] >= 1.0:
        # Passer à l'arrêt suivant
        bus["position_arret_actuel"] = bus["position_arret_suivant"]
        bus["position_arret_suivant"] = (bus["position_arret_suivant"] + 1) % len(arrets)
        bus["progression"] = bus["progression"] - 1.0
        
        # Simuler l'arrêt au prochain passage (attente aux arrêts)
        if random.random() < 0.8:  # 80% de chance de s'arrêter
            bus["progression"] = 0.0  # Positionner juste au début du tronçon
        
        # Mettre à jour le nombre de passagers
        variation_passagers = random.randint(-10, 10)
        bus["passagers"] = max(0, min(bus["capacite"], bus["passagers"] + variation_passagers))

def mettre_a_jour_position_taxi(taxi, delta_temps):
    """Met à jour la position d'un taxi selon sa vitesse et le temps écoulé."""
    # Si le taxi n'est pas en mouvement, ne pas modifier sa position
    if not taxi["en_mouvement"]:
        # Chance de commencer à se déplacer
        if random.random() < 0.1:  # 10% de chance par intervalle
            taxi["en_mouvement"] = True
            zone = ZONES_TAXIS[taxi["zone"]]
            
            # Nouvelle destination aléatoire dans la zone
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, zone["rayon"])
            
            lat_km = 111.32
            lon_km = 111.32 * math.cos(math.radians(zone["centre"]["latitude"]))
            
            nouvelle_latitude = zone["centre"]["latitude"] + (distance * math.sin(angle)) / lat_km
            nouvelle_longitude = zone["centre"]["longitude"] + (distance * math.cos(angle)) / lon_km
            
            taxi["destination"] = {
                "latitude": nouvelle_latitude,
                "longitude": nouvelle_longitude
            }
            
            # Vitesse aléatoire
            taxi["vitesse"] = random.uniform(20, 50)
        return
    
    if not taxi["destination"]:
        # Si pas de destination mais en mouvement, créer une destination
        zone = ZONES_TAXIS[taxi["zone"]]
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, zone["rayon"])
        
        lat_km = 111.32
        lon_km = 111.32 * math.cos(math.radians(zone["centre"]["latitude"]))
        
        nouvelle_latitude = zone["centre"]["latitude"] + (distance * math.sin(angle)) / lat_km
        nouvelle_longitude = zone["centre"]["longitude"] + (distance * math.cos(angle)) / lon_km
        
        taxi["destination"] = {
            "latitude": nouvelle_latitude,
            "longitude": nouvelle_longitude
        }
        return
    
    # Calculer la distance jusqu'à la destination
    position_actuelle = {"latitude": taxi["latitude"], "longitude": taxi["longitude"]}
    distance_totale = calculer_distance_gps(position_actuelle, taxi["destination"])
    
    # Si très proche de la destination, considérer comme arrivé
    if distance_totale < 0.05:  # Moins de 50 mètres
        # Arrivé à destination
        taxi["en_mouvement"] = False
        taxi["vitesse"] = 0
        taxi["destination"] = None
        
        # Mettre à jour la disponibilité
        taxi["disponible"] = random.random() < 0.7
        return
    
    # Calculer le déplacement
    vitesse_km_s = taxi["vitesse"] / 3600  # Convertir km/h en km/s
    distance_parcourue = vitesse_km_s * delta_temps  # Distance parcourue en km
    
    # S'assurer de ne pas dépasser la destination
    progression = min(1.0, distance_parcourue / distance_totale)
    
    # Calculer la nouvelle position
    nouvelle_position = interpoler_position(position_actuelle, taxi["destination"], progression)
    taxi["latitude"] = nouvelle_position["latitude"]
    taxi["longitude"] = nouvelle_position["longitude"]
    
    # Ajuster légèrement la vitesse pour la simulation
    taxi["vitesse"] = taxi["vitesse"] * (0.95 + random.random() * 0.1)  # Variation de ±5%

def generer_donnees_bus(bus):
    """Génère des données complètes pour un bus."""
    ligne = LIGNES_BUS[bus["ligne"]]
    arrets = ligne["arrets"]
    
    # Position actuelle interpolée
    arret_actuel = arrets[bus["position_arret_actuel"]]
    arret_suivant = arrets[bus["position_arret_suivant"]]
    position = interpoler_position(arret_actuel, arret_suivant, bus["progression"])
    
    # Calculer l'heure estimée d'arrivée au prochain arrêt
    distance_restante = calculer_distance_gps(
        position, 
        arret_suivant
    )
    temps_estime_secondes = (distance_restante / bus["vitesse"]) * 3600 if bus["vitesse"] > 0 else 0
    
    # Retard simulé (en minutes)
    retard = 0
    if random.random() < 0.3:  # 30% de chance d'avoir du retard
        retard = random.randint(1, 10)
    
    return {
        "id": bus["id"],
        "ligne": bus["ligne"],
        "nom_ligne": bus["nom_ligne"],
        "latitude": position["latitude"],
        "longitude": position["longitude"],
        "vitesse": round(bus["vitesse"], 1),
        "en_service": bus["en_service"],
        "arret_actuel": arrets[bus["position_arret_actuel"]]["nom"],
        "arret_suivant": arrets[bus["position_arret_suivant"]]["nom"],
        "passagers": bus["passagers"],
        "capacite": bus["capacite"],
        "taux_occupation": round(bus["passagers"] / bus["capacite"] * 100),
        "temps_estime_prochain_arret": round(temps_estime_secondes),
        "retard": retard,
        "timestamp": time.time()
    }

def generer_donnees_taxi(taxi):
    """Génère des données complètes pour un taxi."""
    return {
        "id": taxi["id"],
        "zone": taxi["zone"],
        "nom_zone": taxi["nom_zone"],
        "latitude": taxi["latitude"],
        "longitude": taxi["longitude"],
        "vitesse": round(taxi["vitesse"], 1),
        "disponible": taxi["disponible"],
        "en_mouvement": taxi["en_mouvement"],
        "destination": taxi["destination"],
        "timestamp": time.time()
    }

def publier(client):
    """Publie périodiquement les données de tous les véhicules."""
    derniere_publication = time.time()
    
    while True:
        try:
            temps_actuel = time.time()
            delta_temps = temps_actuel - derniere_publication
            derniere_publication = temps_actuel
            
            # Mettre à jour les positions des bus
            for bus in BUS:
                mettre_a_jour_position_bus(bus, delta_temps)
                donnees = generer_donnees_bus(bus)
                message = json.dumps(donnees, ensure_ascii=False)
                topic = f"{TOPIC_TRANSPORT}/bus/{bus['id']}"
                result = client.publish(topic, message)
                
                # Vérification de la publication
                statut = result[0]
                if statut == 0:
                    print(f"Message envoyé au topic {topic}")
                else:
                    print(f"Échec d'envoi du message au topic {topic}")
                
                # Petit délai entre chaque publication
                time.sleep(0.1)
            
            # Mettre à jour les positions des taxis
            for taxi in TAXIS:
                mettre_a_jour_position_taxi(taxi, delta_temps)
                donnees = generer_donnees_taxi(taxi)
                message = json.dumps(donnees, ensure_ascii=False)
                topic = f"{TOPIC_TRANSPORT}/taxi/{taxi['id']}"
                result = client.publish(topic, message)
                
                # Vérification de la publication
                statut = result[0]
                if statut == 0:
                    print(f"Message envoyé au topic {topic}")
                else:
                    print(f"Échec d'envoi du message au topic {topic}")
                
                # Petit délai entre chaque publication
                time.sleep(0.1)
            
            # Attente avant la prochaine série de publications
            time.sleep(INTERVALLE_TRANSPORT)
            
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(5)  # Attente en cas d'erreur avant de réessayer

def executer():
    """Fonction principale du simulateur."""
    client = connecter_mqtt()
    client.loop_start()
    publier(client)

if __name__ == '__main__':
    print("Démarrage du simulateur de capteurs de transport public...")
    executer()
