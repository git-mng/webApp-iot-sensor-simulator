# Fichier: config.py
# Configuration commune pour tous les capteurs IoT

# Configuration du broker MQTT
BROKER_ADRESSE = "localhost"  # Adresse du broker MQTT
BROKER_PORT = 1883            # Port par défaut pour MQTT
CLIENT_ID_BASE = "capteur_iot_"  # Base pour l'ID client MQTT

# Topics MQTT
TOPIC_PARKING = "iot/parking/disponibilite"
TOPIC_BATIMENTS = "iot/batiments/info"
TOPIC_WIFI = "iot/wifi/etat"
TOPIC_METEO = "iot/meteo/conditions"
TOPIC_TRANSPORT = "iot/transport/position"

# Intervalles de publication (en secondes)
INTERVALLE_PARKING = 60       # Mise à jour chaque minute
INTERVALLE_BATIMENTS = 60    # Mise à jour toutes les 5 minutes
INTERVALLE_WIFI = 30          # Mise à jour toutes les 30 secondes
INTERVALLE_METEO = 120        # Mise à jour toutes les 2 minutes
INTERVALLE_TRANSPORT = 15     # Mise à jour toutes les 15 secondes
