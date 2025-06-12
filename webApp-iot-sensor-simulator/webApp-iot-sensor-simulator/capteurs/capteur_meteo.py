#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulateur de capteurs météorologiques.
Ce script génère des données météorologiques simulées et les publie sur un topic MQTT.
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

# Ajout du répertoire parent au path pour importer config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BROKER_ADRESSE, BROKER_PORT, CLIENT_ID_BASE, TOPIC_METEO, INTERVALLE_METEO

# Liste des stations météo à simuler
STATIONS_METEO = [
    {"id": "METEO001", "nom": "Station Campus Principal", "latitude": 48.8566, "longitude": 2.3522},
    {"id": "METEO002", "nom": "Station Annexe Nord", "latitude": 48.8606, "longitude": 2.3376},
    {"id": "METEO003", "nom": "Station Annexe Sud", "latitude": 48.8496, "longitude": 2.3523}
]

# États possibles du ciel
ETATS_CIEL = ["Ensoleillé", "Partiellement nuageux", "Nuageux", "Couvert", "Brumeux", 
              "Pluvieux", "Orageux", "Neigeux"]

# Tendances météo pour simuler une évolution réaliste
tendance_temperature = random.uniform(-0.5, 0.5)  # Tendance de variation par heure
tendance_humidite = random.uniform(-2, 2)  # Tendance de variation par heure
derniere_meteo = {}  # Pour stocker les dernières valeurs générées par station

def connecter_mqtt():
    """Établit une connexion au broker MQTT."""
    # Génération d'un ID client unique
    id_client = f"{CLIENT_ID_BASE}meteo_{str(uuid.uuid4())[:8]}"
    
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

def initialiser_meteo():
    """Initialise les données météo pour toutes les stations."""
    global derniere_meteo
    
    # Obtenir le mois actuel pour des données saisonnières réalistes
    mois_actuel = datetime.now().month
    
    # Températures de base selon la saison (hémisphère nord)
    if 3 <= mois_actuel <= 5:  # Printemps
        temp_base = random.uniform(10, 20)
    elif 6 <= mois_actuel <= 8:  # Été
        temp_base = random.uniform(20, 30)
    elif 9 <= mois_actuel <= 11:  # Automne
        temp_base = random.uniform(8, 18)
    else:  # Hiver
        temp_base = random.uniform(-5, 10)
    
    # Initialiser les données pour chaque station
    for station in STATIONS_METEO:
        # Légère variation entre stations
        temp_variation = random.uniform(-2, 2)
        temperature = round(temp_base + temp_variation, 1)
        
        humidite = random.randint(30, 90)
        pression = random.uniform(990, 1030)
        
        # L'état du ciel est influencé par l'humidité
        if humidite > 80:
            etats_possibles = ["Couvert", "Pluvieux", "Brumeux", "Orageux"]
        elif humidite > 60:
            etats_possibles = ["Partiellement nuageux", "Nuageux", "Couvert"]
        else:
            etats_possibles = ["Ensoleillé", "Partiellement nuageux"]
        
        etat_ciel = random.choice(etats_possibles)
        
        # Vitesse du vent (en km/h)
        vitesse_vent = round(random.uniform(0, 30), 1)
        
        # Direction du vent (en degrés)
        direction_vent = random.randint(0, 359)
        
        # Précipitations (en mm)
        if etat_ciel in ["Pluvieux", "Orageux", "Neigeux"]:
            precipitations = round(random.uniform(0.1, 15), 1)
        else:
            precipitations = 0.0
        
        derniere_meteo[station["id"]] = {
            "temperature": temperature,
            "humidite": humidite,
            "pression": pression,
            "etat_ciel": etat_ciel,
            "vitesse_vent": vitesse_vent,
            "direction_vent": direction_vent,
            "precipitations": precipitations
        }

def generer_donnees_meteo(station):
    """Génère des données météorologiques évolutives pour une station."""
    global tendance_temperature, tendance_humidite, derniere_meteo
    
    # Si les données n'ont pas été initialisées
    if station["id"] not in derniere_meteo:
        initialiser_meteo()
    
    derniere = derniere_meteo[station["id"]]
    
    # Faire évoluer la température avec une tendance et une variation aléatoire
    variation_temp = random.uniform(-0.3, 0.3) + tendance_temperature * (INTERVALLE_METEO / 3600)
    nouvelle_temperature = derniere["temperature"] + variation_temp
    # Limiter à des valeurs réalistes
    nouvelle_temperature = max(-30, min(45, nouvelle_temperature))
    
    # Faire évoluer l'humidité
    variation_humidite = random.uniform(-2, 2) + tendance_humidite * (INTERVALLE_METEO / 3600)
    nouvelle_humidite = derniere["humidite"] + variation_humidite
    # Limiter à des valeurs réalistes
    nouvelle_humidite = max(10, min(100, nouvelle_humidite))
    
    # Faire évoluer la pression
    variation_pression = random.uniform(-0.5, 0.5)
    nouvelle_pression = derniere["pression"] + variation_pression
    # Limiter à des valeurs réalistes
    nouvelle_pression = max(950, min(1050, nouvelle_pression))
    
    # Faire évoluer le vent
    variation_vent = random.uniform(-2, 2)
    nouvelle_vitesse_vent = max(0, derniere["vitesse_vent"] + variation_vent)
    nouvelle_direction_vent = (derniere["direction_vent"] + random.randint(-10, 10)) % 360
    
    # L'état du ciel peut changer en fonction des autres paramètres
    if random.random() < 0.1:  # 10% de chance de changement
        # Probabilité basée sur l'humidité
        if nouvelle_humidite > 80:
            etats_possibles = ["Couvert", "Pluvieux", "Brumeux", "Orageux"]
        elif nouvelle_humidite > 60:
            etats_possibles = ["Partiellement nuageux", "Nuageux", "Couvert"]
        else:
            etats_possibles = ["Ensoleillé", "Partiellement nuageux"]
        
        nouvel_etat_ciel = random.choice(etats_possibles)
    else:
        nouvel_etat_ciel = derniere["etat_ciel"]
    
    # Précipitations basées sur l'état du ciel
    if nouvel_etat_ciel in ["Pluvieux", "Orageux"]:
        nouvelles_precipitations = max(0, derniere["precipitations"] + random.uniform(-1, 2))
    elif nouvel_etat_ciel == "Neigeux":
        nouvelles_precipitations = max(0, derniere["precipitations"] + random.uniform(-0.5, 1))
    else:
        nouvelles_precipitations = max(0, derniere["precipitations"] - random.uniform(0, 0.5))
    
    # Mettre à jour les dernières données
    derniere_meteo[station["id"]] = {
        "temperature": round(nouvelle_temperature, 1),
        "humidite": round(nouvelle_humidite),
        "pression": round(nouvelle_pression, 1),
        "etat_ciel": nouvel_etat_ciel,
        "vitesse_vent": round(nouvelle_vitesse_vent, 1),
        "direction_vent": nouvelle_direction_vent,
        "precipitations": round(nouvelles_precipitations, 1)
    }
    
    # Créer le message complet
    donnees = {
        "id": station["id"],
        "nom": station["nom"],
        "latitude": station["latitude"],
        "longitude": station["longitude"],
        "temperature": derniere_meteo[station["id"]]["temperature"],
        "humidite": derniere_meteo[station["id"]]["humidite"],
        "pression": derniere_meteo[station["id"]]["pression"],
        "etat_ciel": derniere_meteo[station["id"]]["etat_ciel"],
        "vitesse_vent": derniere_meteo[station["id"]]["vitesse_vent"],
        "direction_vent": derniere_meteo[station["id"]]["direction_vent"],
        "precipitations": derniere_meteo[station["id"]]["precipitations"],
        "timestamp": time.time()
    }
    
    return donnees

def publier(client):
    """Publie périodiquement les données de toutes les stations météo."""
    # Initialiser les données météo au démarrage
    initialiser_meteo()
    
    # Boucle de publication
    while True:
        try:
            for station in STATIONS_METEO:
                donnees = generer_donnees_meteo(station)
                message = json.dumps(donnees, ensure_ascii=False)
                topic = f"{TOPIC_METEO}/{station['id']}"
                result = client.publish(topic, message)
                
                # Vérification de la publication
                statut = result[0]
                if statut == 0:
                    print(f"Message envoyé au topic {topic}")
                else:
                    print(f"Échec d'envoi du message au topic {topic}")
                
                # Petit délai entre chaque station
                time.sleep(0.5)
                
            # Faire évoluer légèrement les tendances
            global tendance_temperature, tendance_humidite
            tendance_temperature += random.uniform(-0.1, 0.1)
            tendance_temperature = max(-1, min(1, tendance_temperature))
            tendance_humidite += random.uniform(-0.5, 0.5)
            tendance_humidite = max(-3, min(3, tendance_humidite))
            
            # Attente avant la prochaine série de publications
            time.sleep(INTERVALLE_METEO)
            
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(5)  # Attente en cas d'erreur avant de réessayer

def executer():
    """Fonction principale du simulateur."""
    client = connecter_mqtt()
    client.loop_start()
    publier(client)

if __name__ == '__main__':
    print("Démarrage du simulateur de capteurs météorologiques...")
    executer()
