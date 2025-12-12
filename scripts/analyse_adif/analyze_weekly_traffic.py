import re
from datetime import datetime
from collections import defaultdict

# --- Configuration ---
ADIF_FILE_PATH = 'f4lno.adif'
# ---------------------

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

# Liste des jours de la semaine (pour l'affichage)
DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'] # 0=Lundi, 6=Dimanche

def analyze_weekly_traffic(file_path):
    # Stockage : {bande: [contacts_lundi, contacts_mardi, ..., contacts_dimanche]}
    weekly_band_counts = defaultdict(lambda: [0] * 7)
    all_bands = set()
    total_contacts = 0
    
    # Regex
    re_date = re.compile(r'<QSO_DATE:\d+>(\d{8})') 
    re_freq = re.compile(r'<FREQ:\d+>([\d.]+)') 

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().upper()
            records = content.split('<EOR>')
            
            for record in records:
                if not record.strip(): continue

                total_contacts += 1

                # 1. Extraction
                match_date = re_date.search(record)
                match_freq = re_freq.search(record)

                if not (match_date and match_freq):
                    continue
                
                qso_date_str = match_date.group(1)
                freq_mhz = float(match_freq.group(1))
                band = get_band_from_frequency(freq_mhz)
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

    except FileNotFoundError:
        print(f"ERREUR: Le fichier {ADIF_FILE_PATH} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")

# --- Exécution ---
if __name__ == "__main__":
    analyze_weekly_traffic(ADIF_FILE_PATH)
