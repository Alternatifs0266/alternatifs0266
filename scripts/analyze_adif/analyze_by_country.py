""" Analyse les contacts ADIF par pays/DXCC et par bande. """
import re
import os
from collections import defaultdict
from cty import CTY
import common

# --- Fonction d'Analyse Principale ---

def analyze_contacts_by_band_country(adif_records, cty_dat_path=None):
    """ Analyse les contacts ADIF par pays/DXCC et par bande. """
    # Chargement du fichier cty.dat si fourni et disponible (pour recherche de pays par callsign)
    cty = CTY(cty_dat_path) if cty_dat_path and os.path.exists(cty_dat_path) else None


    # Structure de stockage :
    # {
    #     "Japan": {"17m": 12, "15m": 5, "12m": 4},
    #     "China": {"17m": 10, "15m": 3, "12m": 2},
    #     ...
    # }
    contacts_by_country = defaultdict(lambda: defaultdict(int))
    total_count = 0

    # Regex pour extraire les champs
    re_call = re.compile(r'<CALL:\d+>([A-Z0-9/]+)')
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)')
    re_grid = re.compile(r'<GRIDSQUARE:\d+>([A-Z]{2}\d{2}[A-Z]{0,2})')
    # NOUVELLE REGEX pour le Pays/DXCC
    # On cherche le tag <COUNTRY:n> suivi du nom, jusqu'à la balise suivante <
    re_country = re.compile(r'<COUNTRY:\d+>(.+?)<')

    for record in adif_records:
        if not record.strip():
            continue

        # 1. Extraction des champs
        match_call = re_call.search(record)
        match_freq = re_freq.search(record)
        match_grid = re_grid.search(record)
        match_country = re_country.search(record) # Extraction du pays

        if not (match_call and match_freq) or (not match_grid and cty is None):
            continue

        # Nettoyage des données
        callsign = match_call.group(1).strip()
        freq_mhz = float(match_freq.group(1))
        band = common.get_band_from_frequency(freq_mhz)

        # Pays : utilisation de la valeur trouvée sinon recherche via cty.dat
        if match_country:
            country = match_country.group(1).strip().title()
        elif cty:
            # Recherche du pays dans le fichier cty.dat
            country, _, _ = cty.callsign_lookup(callsign)
        else:
            country = "ND"

        # Ajout du contact au pays correspondant
        contacts_by_country[country][band] += 1
        total_count += 1

    # Affichage des résultats
    print("\n--- Analyse des Contacts par Pays/DXCC et par Bande ---")
    header = f"{'Pays/DXCC':<25} |{'Total':>6}|" + " |".join(f"{band:>5}" for band in common.ALL_BANDS) + " |"
    separator = "-" * len(header)
    print(header)
    print(separator)
    sorted_countries = dict(sorted(contacts_by_country.items()))
    for country, bands in sorted_countries.items():
        counts = [bands.get(band, 0) for band in common.ALL_BANDS]
        row = f"{country[:25]:<25} | {sum(bands.values()):4}" + " | " + " | ".join(f"{count:4}" for count in counts) + " |"
        print(row)
    print(separator)
    print(f"{'Total':<25} | {total_count:4}" + " | " + " | ".join(f"{sum(bands.get(band, 0) for bands in sorted_countries.values()):4}" for band in common.ALL_BANDS) + " |\n")
    print(separator)


# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Analyse les contacts ADIF par pays/DXCC et par bande.")
    try:
        records = common.read_file_content(args.file)
        analyze_contacts_by_band_country(records, cty_dat_path=args.ctydat)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution: {e}")
