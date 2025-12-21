""" Analyse de Performance DX (Mode et Bande) """
import re
from collections import defaultdict
import common

# --- Fonction d'Analyse Principale ---

def analyze_dx_performance(adif_records, my_locator):
    """ Analyse la performance DX par mode et bande à partir des enregistrements ADIF. """
    # my_loc_lat, my_loc_lon sont calculés une seule fois
    my_loc_lat, my_loc_lon = common.locator_to_latlon(my_locator)

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

    for record in adif_records:
        if not record.strip():
            continue

        total_contacts += 1

        # 1. Extraction
        match_mode = re_mode.search(record)
        match_freq = re_freq.search(record)
        match_grid = re_grid.search(record)

        if not (match_mode and match_freq and match_grid):
            continue

        mode = match_mode.group(1).strip()
        freq_mhz = float(match_freq.group(1))
        band = common.get_band_from_frequency(freq_mhz)
        other_locator = match_grid.group(1).strip()

        if len(other_locator) < 4:
            continue # Nécessite au moins 4 caractères pour le calcul

        contacts_with_locators += 1

        # 2. Calcul de la distance
        other_lat, other_lon = common.locator_to_latlon(other_locator)
        if other_lat is None:
            continue

        distance_km = common.haversine_distance(my_loc_lat, my_loc_lon, other_lat, other_lon)

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

# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Analyse de Performance DX (Mode et Bande)")
    try:
        records = common.read_file_content(args.file)
        analyze_dx_performance(records, args.locator)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")
