import re
import math
from collections import defaultdict

# --- Configuration Nécessaire ---
ADIF_FILE_PATH = 'f4lno.adif'
# VEUILLEZ RENSEIGNER VOTRE PROPRE LOCALISATEUR QRA (ex: 'JN33')
# Cela permet de calculer la distance de chaque contact.
MY_LOCATOR = 'JN33' # <--- REMPLACEZ PAR VOTRE VRAI LOCALISATEUR QRA (6 chiffres si possible)
# -------------------------------

# Mappage des fréquences vers les bandes
def get_band_from_frequency(freq_mhz):
    if 1.8 <= freq_mhz < 2: return '160m'
    elif 3.5 <= freq_mhz < 4: return '80m'
    elif 7 <= freq_mhz < 8: return '40m'
    elif 10 <= freq_mhz < 11: return '30m'
    elif 14 <= freq_mhz < 15: return '20m'
    elif 18 <= freq_mhz < 19: return '17m'
    elif 21 <= freq_mhz < 22: return '15m'
    elif 24 <= freq_mhz < 25: return '12m'
    elif 28 <= freq_mhz < 30: return '10m'
    elif 50 <= freq_mhz < 54: return '6m'
    else: return 'Autres'

# --- Fonctions de Géolocalisation et Distance ---

def locator_to_latlon(locator):
    """Convertit un localisateur QRA (4 ou 6 chars) en (Latitude, Longitude)"""
    locator = locator.upper().strip()
    if len(locator) < 4:
        return None, None

    # Conversion de base (Field et Square)
    lon = (ord(locator[0]) - ord('A')) * 20 - 180
    lat = (ord(locator[1]) - ord('A')) * 10 - 90
    lon += (int(locator[2])) * 2
    lat += (int(locator[3])) * 1

    # Conversion des Subsquares (6 chars)
    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord('A')) * (2/24)
        lat += (ord(locator[5]) - ord('A')) * (1/24)
        # Centrage du point dans le subsquare pour plus de précision
        lon += 1/24 
        lat += 0.5/24 
    # Centrage du point dans le square pour les 4 chars
    elif len(locator) == 4:
        lon += 1.0
        lat += 0.5

    return lat, lon

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux points Lat/Lon (Formule Haversine)"""
    R = 6371  # Rayon de la Terre en kilomètres
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# --- Fonction d'Analyse Principale ---

def analyze_dx_performance(file_path, my_locator):
    # my_loc_lat, my_loc_lon sont calculés une seule fois
    my_loc_lat, my_loc_lon = locator_to_latlon(my_locator)

    if my_loc_lat is None:
        print(f"ERREUR: Localisateur QRA '{my_locator}' invalide ou trop court. Le programme s'arrête.")
        return

    # Structure de stockage : {(band, mode): {'distances': [list], 'count': int}}
    dx_data = defaultdict(lambda: {'distances': [], 'count': 0})
    total_contacts = 0
    contacts_with_locators = 0
    
    # Regex pour extraire les champs
    re_mode = re.compile(r'<MODE:\d+>([A-Z0-9]+)') 
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)') 
    re_grid = re.compile(r'<GRIDSQUARE:\d+>([A-Z]{2}\d{2}[A-Z]{0,2})') # Capture jusqu'à 6 chars (ex: JN33AA)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().upper()
            records = content.split('<EOR>')
            
            for record in records:
                if not record.strip(): continue

                total_contacts += 1

                # 1. Extraction
                match_mode = re_mode.search(record)
                match_freq = re_freq.search(record)
                match_grid = re_grid.search(record)

                if not (match_mode and match_freq and match_grid):
                    continue
                
                mode = match_mode.group(1).strip()
                freq_mhz = float(match_freq.group(1))
                band = get_band_from_frequency(freq_mhz)
                other_locator = match_grid.group(1).strip()

                if len(other_locator) < 4:
                    continue # Nécessite au moins 4 caractères pour le calcul

                contacts_with_locators += 1

                # 2. Calcul de la distance
                other_lat, other_lon = locator_to_latlon(other_locator)
                if other_lat is None:
                    continue 

                distance_km = haversine_distance(my_loc_lat, my_loc_lon, other_lat, other_lon)

                # 3. Agrégation
                key = (band, mode)
                dx_data[key]['distances'].append(distance_km)
                dx_data[key]['count'] += 1

        # --- Calcul des Résultats Finals ---
        results = []
        for (band, mode), data in dx_data.items():
            if data['count'] > 0:
                avg_distance = sum(data['distances']) / data['count']
                results.append({
                    'band': band,
                    'mode': mode,
                    'count': data['count'],
                    'avg_distance': avg_distance
                })

        # Trier les résultats par distance moyenne (du plus grand au plus petit)
        results.sort(key=lambda x: x['avg_distance'], reverse=True)

        # --- Affichage ---
        print("\n--- Analyse de Performance DX (Mode et Bande) ---")
        print(f"Localisateur QRA de la station : {my_locator}")
        print(f"Total des contacts analysés : {total_contacts}")
        print(f"Contacts avec localisateur QRA : {contacts_with_locators}\n")

        header = f"{'Bande':<6} | {'Mode':<6} | {'Contacts':<8} | {'Distance Moyenne (km)':<25}"
        separator = "-" * len(header)
        
        print("Classement des Combinaisons (Mode / Bande) par Performance DX :")
        print(separator)
        print(header)
        print(separator)
        
        for item in results:
            row = (
                f"{item['band']:<6} | "
                f"{item['mode']:<6} | "
                f"{item['count']:<8} | "
                f"{item['avg_distance']:<25.2f}"
            )
            print(row)

        print(separator)
        print("\n*La Distance Moyenne (km) est l'indicateur clé de la performance DX.")

    except FileNotFoundError:
        print(f"ERREUR: Le fichier {ADIF_FILE_PATH} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")

# --- Exécution ---
if __name__ == "__main__":
    analyze_dx_performance(ADIF_FILE_PATH, MY_LOCATOR)
