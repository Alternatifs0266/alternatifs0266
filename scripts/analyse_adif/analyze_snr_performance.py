""" Analyse de la Performance SNR à partir d'un fichier ADIF."""
import re
from collections import defaultdict
import common


def analyze_snr(adif_records):
    """ Analyse la performance SNR par mode et bande à partir des enregistrements ADIF. """
    # Stockage : {(band, mode): {'snr_sum': float, 'count': int}}
    snr_data = defaultdict(lambda: {'snr_sum': 0.0, 'count': 0})
    total_contacts = 0
    contacts_with_snr = 0

    # Regex pour extraire les champs
    re_mode = re.compile(r'<MODE:\d+>([A-Z0-9]+)')
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)')

    # *** NOUVELLE REGEX POUR APP_PSKREP_SNR ou RST_RCVD de WSJTX ***
    # On cherche <APP_PSKREP_SNR:n> suivi d'un nombre (potentiellement négatif ou positif).
    # re_snr = re.compile(r'<APP_PSKREP_SNR:\d+:?[A-Z]*>([-+]?\d+)|<RST_RCVD:\d+>([-+]?\d+)')
    re_snr = re.compile(r'(?:<APP_PSKREP_SNR:\d+:?[A-Z]*>|<RST_RCVD:\d+>)([-+]?\d+)')

    for record in adif_records:
        if not record.strip():
            continue

        total_contacts += 1

        # 1. Extraction
        match_mode = re_mode.search(record)
        match_freq = re_freq.search(record)
        match_snr = re_snr.search(record)

        if not (match_mode and match_freq and match_snr):
            continue

        mode = match_mode.group(1).strip()
        freq_mhz = float(match_freq.group(1))
        band = common.get_band_from_frequency(freq_mhz)

        # Le SNR est extrait de APP_PSKREP_SNR. Conversion en float.
        try:
            # Assurez-vous que la valeur est numérique (ex: -12, 5)
            snr_value = float(match_snr.group(1))
        except ValueError:
            continue

        contacts_with_snr += 1

        # 2. Agrégation
        key = (band, mode)
        snr_data[key]['snr_sum'] += snr_value
        snr_data[key]['count'] += 1

    # --- Calcul des Résultats Finals ---
    results = []
    for (band, mode), data in snr_data.items():
        if data['count'] >= 10: # Minimum de 10 contacts pour une moyenne fiable
            avg_snr = data['snr_sum'] / data['count']
            results.append({
                'band': band,
                'mode': mode,
                'count': data['count'],
                'avg_snr': avg_snr
            })

    # Trier les résultats par SNR moyen (du plus grand au plus petit)
    results.sort(key=lambda x: x['avg_snr'], reverse=True)

    # --- Affichage ---
    print("\n--- Analyse de Qualité du Signal (SNR) par Mode et Bande ---")
    print(f"Total des contacts analysés : {total_contacts}")
    print(f"Contacts avec une valeur SNR (numérique via APP_PSKREP_SNR ou RST_RCVD) : {contacts_with_snr}\n")

    header = f"{'Bande':<6} | {'Mode':<6} | {'Contacts':<8} | {'SNR Moyen (dB)':<20}"
    separator = "-" * len(header)

    print("Classement des Combinaisons par SNR Moyen (Moyenne calculée avec >= 10 contacts) :")
    print(separator)
    print(header)
    print(separator)

    for item in results:
        row = (
            f"{item['band']:<6} | "
            f"{item['mode']:<6} | "
            f"{item['count']:<8} | "
            f"{item['avg_snr']:<20.2f}"
        )
        print(row)

    print(separator)
    print("\n*Un SNR positif ou proche de zéro (dB) indique une excellente qualité de signal.")


# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Analyse de la Performance SNR")
    try:
        records = common.read_file_content(args.file)
        analyze_snr(records)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")
