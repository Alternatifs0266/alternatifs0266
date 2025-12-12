import re
import math
from pprint import pprint

# --- Configuration Nécessaire ---
ADIF_FILE_PATH = 'f4lno.adif'
# VEUILLEZ RENSEIGNER VOTRE PROPRE LOCALISATEUR QRA (ex: 'JN33')
MY_LOCATOR = 'JN33' # <--- REMPLACEZ PAR VOTRE VRAI LOCALISATEUR QRA (4 ou 6 chiffres)
# -------------------------------

# --- Fonctions de Géolocalisation et Distance (Identiques au script précédent) ---

def locator_to_latlon(locator):
    """Convertit un localisateur QRA (4 ou 6 chars) en (Latitude, Longitude)"""
    locator = locator.upper().strip()
    if len(locator) < 4:
        return None, None

    lon = (ord(locator[0]) - ord('A')) * 20 - 180
    lat = (ord(locator[1]) - ord('A')) * 10 - 90
    lon += (int(locator[2])) * 2
    lat += (int(locator[3])) * 1

    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord('A')) * (2/24) + (1/24)
        lat += (ord(locator[5]) - ord('A')) * (1/24) + (0.5/24)
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

def find_top_dx(file_path, my_locator, top_n=1000):
    my_loc_lat, my_loc_lon = locator_to_latlon(my_locator)

    if my_loc_lat is None:
        print(f"ERREUR: Localisateur QRA '{my_locator}' invalide ou trop court. Le programme s'arrête.")
        return

    all_contacts_data = []
    total_contacts = 0
    contacts_with_locators = 0
    
    # Regex pour extraire les champs
    re_call = re.compile(r'<CALL:\d+>([A-Z0-9/]+)')
    re_mode = re.compile(r'<MODE:\d+>([A-Z0-9]+)') 
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)') 
    re_grid = re.compile(r'<GRIDSQUARE:\d+>([A-Z]{2}\d{2}[A-Z]{0,2})')
    # NOUVELLE REGEX pour le Pays/DXCC
    # On cherche le tag <COUNTRY:n> suivi du nom, jusqu'à la balise suivante <
    re_country = re.compile(r'<COUNTRY:\d+>(.+?)<') 

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().upper() # Lecture du fichier
            records = content.split('<EOR>')
            
            for record in records:
                if not record.strip(): continue

                total_contacts += 1

                # 1. Extraction des champs
                match_call = re_call.search(record)
                match_mode = re_mode.search(record)
                match_freq = re_freq.search(record)
                match_grid = re_grid.search(record)
                match_country = re_country.search(record) # Extraction du pays

                if not (match_call and match_mode and match_freq and match_grid):
                    continue
                
                # Nettoyage des données
                callsign = match_call.group(1).strip()
                mode = match_mode.group(1).strip()
                freq_mhz = float(match_freq.group(1))
                other_locator = match_grid.group(1).strip()
                
                # Pays : utilisation de la valeur trouvée ou "ND" (Non Disponible)
                country = match_country.group(1).strip().title() if match_country else "ND"

                if len(other_locator) < 4:
                    continue

                contacts_with_locators += 1

                # 2. Calcul de la distance
                other_lat, other_lon = locator_to_latlon(other_locator)
                if other_lat is None:
                    continue 

                distance_km = haversine_distance(my_loc_lat, my_loc_lon, other_lat, other_lon)
                
                # 3. Stockage du contact
                all_contacts_data.append({
                    'distance_km': distance_km,
                    'callsign': callsign,
                    'locator': other_locator,
                    'mode': mode,
                    'freq_mhz': freq_mhz,
                    'country': country # AJOUT DE LA DONNÉE PAYS
                })

        # --- Traitement Final ---
        
        all_contacts_data.sort(key=lambda x: x['distance_km'], reverse=True)
        top_dx = all_contacts_data[:top_n]

        # --- Affichage ---
        print("\n--- Top DX : Les {} Contacts les Plus Éloignés ---".format(len(top_dx)))
        print(f"Position de la station : {my_locator}")
        print(f"Total des contacts lus : {total_contacts}")
        print(f"Contacts avec localisateur QRA : {contacts_with_locators}\n")

        # NOUVEL EN-TÊTE avec Pays/DXCC
        header = f"{'Rang':<4} | {'Distance (km)':<15} | {'Pays/DXCC':<20} | {'Callsign':<10} | {'Locator':<8} | {'Mode':<6} | {'Fréquence (MHz)':<15}"
        separator = "-" * len(header)
        
        print(separator)
        print(header)
        print(separator)
        
        for i, item in enumerate(top_dx, 1):
            # LIGNE DE DONNÉES MISE À JOUR
            row = (
                f"{i:<4} | "
                f"{item['distance_km']:<15.2f} | "
                f"{item['country']:<20} | "
                f"{item['callsign']:<10} | "
                f"{item['locator']:<8} | "
                f"{item['mode']:<6} | "
                f"{item['freq_mhz']:<15.3f}"
            )
            print(row)

        print(separator)

    except FileNotFoundError:
        print(f"ERREUR: Le fichier {ADIF_FILE_PATH} est introuvable. Assurez-vous qu'il est dans le même répertoire.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")

# --- Exécution ---
if __name__ == "__main__":
    find_top_dx(ADIF_FILE_PATH, MY_LOCATOR)
