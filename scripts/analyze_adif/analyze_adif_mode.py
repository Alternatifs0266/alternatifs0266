""" Analyse des Modes par Heure UTC dans un fichier ADIF."""
import re
from collections import defaultdict
import common


def analyze_adif_modes(adif_records):
    """ Analyse la répartition des modes par heure UTC à partir des enregistrements ADIF. """
    # Dictionnaire pour stocker les résultats : {Heure UTC: {Mode: Compte}}
    hourly_mode_counts = defaultdict(lambda: defaultdict(int))
    all_modes = set()
    total_reports = 0

    # Expression régulière pour extraire les champs
    # MODE: cherche <MODE:X>VALUE et capture VALUE
    re_mode = re.compile(r'<MODE:\d+>([A-Z0-9]+)')
    # HEURE: cherche <TIME_ON:X>VALUE et capture VALUE (HHMMSS)
    re_time = re.compile(r'<TIME_ON:\d+>(\d{6})')

    for record in adif_records:
        if not record.strip():
            continue

        # 1. Extraire le mode
        match_mode = re_mode.search(record)
        if not match_mode:
            continue

        mode = match_mode.group(1).strip()
        all_modes.add(mode)

        # 2. Extraire l'heure (HHMMSS)
        match_time = re_time.search(record)
        if not match_time:
            continue

        time_on_str = match_time.group(1)
        # L'heure UTC est les deux premiers chiffres (HH)
        hour_utc = int(time_on_str[:2])

        # 3. Incrémenter le compteur
        hourly_mode_counts[hour_utc][mode] += 1
        total_reports += 1

    print("--- Analyse des Modes par Heure UTC (Fichier ADIF) ---")
    print(f"Total des rapports/contacts analysés: {total_reports}\n")

    # Filtrer et trier les modes (exclure 'NIL' si présent, et trier alphabétiquement)
    sorted_modes = sorted([m for m in all_modes if m and m != 'NIL'])

    if not sorted_modes:
        print("Aucun mode valide trouvé dans les enregistrements analysés.")
        return

    # --- Affichage du Tableau Complet ---

    # 1. Création de l'en-tête du tableau
    header = f"{'Heure':<5} | {'Total':<5} | " + " | ".join(f"{mode:<5}" for mode in sorted_modes)
    separator = "-" * len(header)

    print("Répartition Horaire des Modes (Nombre de Contacts) :")
    print(separator)
    print(header)
    print(separator)

    # 1. Initialisation des compteurs pour les totaux verticaux
    totals_per_mode = [0] * len(sorted_modes)
    grand_total = 0

    # 2. Affichage des lignes de données (Heure par Heure)
    for hour in range(24):
        if hour not in hourly_mode_counts:
            counts = [0] * len(sorted_modes)
            total_hour = 0
        else:
            counts = [hourly_mode_counts[hour].get(mode, 0) for mode in sorted_modes]
            total_hour = sum(counts)

        # Mise à jour des totaux globaux
        grand_total += total_hour
        for i in range(len(counts)):
            totals_per_mode[i] += counts[i]

        # Formater la ligne : Heure | Total | Compte 1 | ...
        row = f"{hour:02}h | {total_hour:<5} | " + " | ".join(f"{count:<5}" for count in counts)
        print(row)

    # 3. Ligne de séparation et ligne finale des TOTAUX
    print("-" * len(row))

    total_row = (
        f"TOT | {grand_total:<5} | " +
        " | ".join(f"{t:<5}" for t in totals_per_mode)
    )
    print(total_row)

    print(separator)
    print(f"\nModes trouvés dans le fichier: {', '.join(sorted_modes)}\n")


# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Analyse des Modes par Heure UTC")
    try:
        records = common.read_file_content(args.file)
        analyze_adif_modes(records)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")
