""" Analyse de la Répartition Horaire des Contacts dans un fichier ADIF."""
import re
from collections import defaultdict
import common


def analyze_adif_log(adif_records):
    """ Analyse la répartition horaire détaillée des contacts par bande à partir des enregistrements ADIF. """
    # Dictionnaire pour stocker les résultats : {Heure UTC: {Bande: Compte}}
    hourly_counts = defaultdict(lambda: defaultdict(int))
    total_reports = 0

    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)')
    re_time = re.compile(r'<TIME_ON:\d+>(\d{6})')

    for record in adif_records:
        if not record.strip():
            continue

        # 1. Extraire la fréquence
        match_freq = re_freq.search(record)
        if not match_freq:
            continue

        freq_mhz = float(match_freq.group(1))
        band = common.get_band_from_frequency(freq_mhz)

        # 2. Extraire l'heure
        match_time = re_time.search(record)
        if not match_time:
            continue

        time_on_str = match_time.group(1)
        hour_utc = int(time_on_str[:2])

        # 3. Incrémenter le compteur
        hourly_counts[hour_utc][band] += 1
        total_reports += 1

    print("--- Analyse Complète des Contacts ADIF ---")
    print(f"Total des rapports/contacts analysés: {total_reports}\n")

    # --- Affichage du Tableau Complet ---

    # 1. Création de l'en-tête du tableau
    header = f"{'Heure':<5} | {'Total':<5} | " + " | ".join(f"{band:<5}" for band in common.ALL_BANDS) + " |"
    separator = "-" * len(header)

    print("Répartition Horaire Détaillée (Nombre de Contacts) :")
    print(separator)
    print(header)
    print(separator)

    # 1. Initialisation des compteurs pour les totaux par bandes
    totals_per_band = [0] * len(common.ALL_BANDS)
    grand_total = 0

    # 2. Affichage des lignes de données (Heure par Heure)
    for hour in range(24):
        if hour not in hourly_counts:
            counts = [0] * len(common.ALL_BANDS)
            total_hour = 0
        else:
            total_hour = sum(hourly_counts[hour].values())
            counts = [hourly_counts[hour].get(band, 0) for band in common.ALL_BANDS]

        # Accumulation des totaux
        grand_total += total_hour
        for i in range(len(counts)):
            totals_per_band[i] += counts[i]

        # Formater la ligne
        row = f"{hour:02}h   | {total_hour:<5} | " + " | ".join(f"{count:<5}" for count in counts) + " |"
        print(row)

    # 3. Affichage de la ligne de TOTAL FINAL
    separator = "-" * len(row)
    print(separator)

    total_row = f"TOTAL | {grand_total:<5} | " + " | ".join(f"{t:<5}" for t in totals_per_band) + " |"
    print(total_row)
    print(separator)

# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Répartition Horaire Détaillée (Nombre de Contacts)")
    try:
        records = common.read_file_content(args.file)
        analyze_adif_log(records)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")
