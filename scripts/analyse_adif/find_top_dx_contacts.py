import re
import math
import os
from pprint import pprint
from cty import CTY
import common

# --- Fonction d'Analyse Principale ---

def find_top_dx(adif_records, my_locator, top_n=1000, cty_dat_path=None):
    my_loc_lat, my_loc_lon = common.locator_to_latlon(my_locator)

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

    # Chargement du fichier cty.dat si fourni et disponible (pour recherche de pays par callsign)
    cty = CTY(cty_dat_path) if cty_dat_path and os.path.exists(cty_dat_path) else None

    for record in adif_records:
        if not record.strip(): continue

        total_contacts += 1

        # 1. Extraction des champs
        match_call = re_call.search(record)
        match_mode = re_mode.search(record)
        match_freq = re_freq.search(record)
        match_grid = re_grid.search(record)
        match_country = re_country.search(record) # Extraction du pays

        if not (match_call and match_mode and match_freq) or (not match_grid and cty is None):
            continue

        # Nettoyage des données
        callsign = match_call.group(1).strip()
        mode = match_mode.group(1).strip()
        freq_mhz = float(match_freq.group(1))
        other_locator = match_grid.group(1).strip() if match_grid else None
        other_lat, other_lon = None, None

        # Pays : utilisation de la valeur trouvée sinon recherche via cty.dat
        if match_country:
            country = match_country.group(1).strip().title()
        elif cty:
            # Recherche du pays dans le fichier cty.dat
            country, lat, lon = cty.callsign_lookup(callsign)
            if not match_grid:
                other_lat, other_lon = float(lat), -float(lon)
                other_locator = common.latlon_to_locator(other_lat, other_lon, precision=6)
        else:
            country = "ND"

        if not other_locator or len(other_locator) < 4:
            continue

        contacts_with_locators += 1

        # 2. Calcul de la distance
        if not other_lat or not other_lon:
            other_lat, other_lon = common.locator_to_latlon(other_locator)
        if other_lat is None:
            continue

        distance_km = common.haversine_distance(my_loc_lat, my_loc_lon, other_lat, other_lon)

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


# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Trouver les Contacts DX les Plus Éloignés")
    try:
        records = common.read_file_content(args.file)
        find_top_dx(records, args.locator, cty_dat_path=args.ctydat)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution: {e}")
