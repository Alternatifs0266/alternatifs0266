import re
from datetime import datetime
from collections import defaultdict
import common


# Liste des jours de la semaine (pour l'affichage)
DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'] # 0=Lundi, 6=Dimanche

def analyze_weekly_traffic(adif_records):
    # Stockage : {bande: [contacts_lundi, contacts_mardi, ..., contacts_dimanche]}
    weekly_band_counts = defaultdict(lambda: [0] * 7)
    all_bands = set()
    total_contacts = 0

    # Regex
    re_date = re.compile(r'<QSO_DATE:\d+>(\d{8})')
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)')

    for record in adif_records:
        if not record.strip(): continue

        total_contacts += 1

        # 1. Extraction
        match_date = re_date.search(record)
        match_freq = re_freq.search(record)

        if not (match_date and match_freq):
            continue

        qso_date_str = match_date.group(1)
        freq_mhz = float(match_freq.group(1))
        band = common.get_band_from_frequency(freq_mhz)
        all_bands.add(band)

        # 2. Déterminer le jour de la semaine
        # L'ADIF utilise le format AAAA MM JJ. La conversion en datetime permet d'obtenir le jour.
        qso_date = datetime.strptime(qso_date_str, '%Y%m%d')
        # weekday() retourne 0 (Lundi) à 6 (Dimanche)
        day_index = qso_date.weekday()

        # 3. Incrémenter le compteur
        weekly_band_counts[band][day_index] += 1

    # --- Affichage des Résultats ---
    print("\n--- Analyse de Tendance du Trafic par Bande et Jour de la Semaine ---")
    print(f"Total des contacts analysés : {total_contacts}\n")

    # 1. Préparer l'en-tête
    sorted_bands = sorted(list(all_bands))
    header_days = " | ".join(f"{day:<10}" for day in DAYS_OF_WEEK)
    header = f"{'Bande':<6} | {header_days} | {'Total':<6}"
    separator = "-" * len(header)

    print("Volume de Contacts par Bande (Répartition Hebdomadaire) :")
    print(separator)
    print(header)
    print(separator)

    # 2. Afficher les données
    for band in sorted_bands:
        counts = weekly_band_counts[band]
        total_band = sum(counts)

        # Formatage des comptes
        counts_str = " | ".join(f"{count:<10}" for count in counts)

        row = (
            f"{band:<6} | "
            f"{counts_str} | "
            f"{total_band:<6}"
        )
        print(row)

    print(separator)


# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Analyse du Trafic Hebdomadaire")
    try:
        records = common.read_file_content(args.file)
        analyze_weekly_traffic(records)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")
