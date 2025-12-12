import re
from collections import defaultdict

# --- Configuration ---
ADIF_FILE_PATH = 'f4lno.adif'

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

def analyze_snr(file_path):
    # Stockage : {(band, mode): {'snr_sum': float, 'count': int}}
    snr_data = defaultdict(lambda: {'snr_sum': 0.0, 'count': 0})
    total_contacts = 0
    contacts_with_snr = 0
    
    # Regex pour extraire les champs
    re_mode = re.compile(r'<MODE:\d+>([A-Z0-9]+)') 
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)') 
    
    # *** NOUVELLE REGEX POUR APP_PSKREP_SNR ***
    # On cherche <APP_PSKREP_SNR:n> suivi d'un nombre (potentiellement négatif ou positif).
    re_snr = re.compile(r'<APP_PSKREP_SNR:\d+:?[A-Z]*>([-+]?\d+)')

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
                match_snr = re_snr.search(record)

                if not (match_mode and match_freq and match_snr):
                    continue
                
                mode = match_mode.group(1).strip()
                freq_mhz = float(match_freq.group(1))
                band = get_band_from_frequency(freq_mhz)
                
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
        print(f"Contacts avec une valeur SNR (numérique via APP_PSKREP_SNR) : {contacts_with_snr}\n")

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

    except FileNotFoundError:
        print(f"ERREUR: Le fichier {ADIF_FILE_PATH} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")

# --- Exécution ---
if __name__ == "__main__":
    analyze_snr(ADIF_FILE_PATH)
