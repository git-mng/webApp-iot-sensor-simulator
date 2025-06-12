# Fichier: config.py
# Configuration pour l'API REST

# Configuration du broker MQTT
BROKER_ADRESSE = "localhost"
BROKER_PORT = 1883
CLIENT_ID_BASE = "api_rest_"

# Topics MQTT à surveiller
TOPICS = [
    "iot/parking/#",
    "iot/batiments/#",
    "iot/wifi/#",
    "iot/meteo/#",
    "iot/transport/#"
]

# Configuration de l'API REST
API_HOST = "0.0.0.0"
API_PORT = 5000

# Période de nettoyage des données anciennes (en secondes)
PERIODE_NETTOYAGE = 3600  # 1 heure

# Durée de conservation des données (en secondes)
DUREE_CONSERVATION = 86400  # 24 heures
