import re
import math
# NOUVEL IMPORT : Ajout de timezone
from datetime import datetime, timedelta, timezone
from astral import LocationInfo
from astral import sun
import common

# --- Distance minimum pour considérer un DX ---
MIN_DX_DISTANCE_KM = 3500
# --- Période de Greyline (minutes avant/après lever/coucher) ---
GREYLINE_WINDOW_MINUTES = 30
# -------------------------------

# --- Fonction d'Analyse Principale ---

def analyze_greyline(file_path, my_locator):
    my_loc_lat, my_loc_lon = common.locator_to_latlon(my_locator)
    if my_loc_lat is None:
        print(f"ERREUR: Localisateur QRA '{my_locator}' invalide ou trop court. Le programme s'arrête.")
        return

    # my_location utilise UTC par défaut
    my_location = LocationInfo("My Station", my_locator, "UTC", my_loc_lat, my_loc_lon)

    # Stockage des résultats
    total_dx_contacts = 0
    greyline_contacts = 0

    # Regex
    re_date = re.compile(r'<QSO_DATE:\d+>(\d{8})')
    re_time = re.compile(r'<TIME_ON:\d+>(\d{6})')
    re_grid = re.compile(r'<GRIDSQUARE:\d+>([A-Z]{2}\d{2}[A-Z]{0,2})')
    re_call = re.compile(r'<CALL:\d+>([A-Z0-9/]+)')

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().upper()
            records = content.split('<EOR>')

            for record in records:
                if not record.strip(): continue

                # Extraction
                match_date = re_date.search(record)
                match_time = re_time.search(record)
                match_grid = re_grid.search(record)
                match_call = re_call.search(record)

                if not (match_date and match_time and match_grid and match_call): continue

                # Conversion Date/Heure : UTILISATION DE timezone.utc
                qso_date_str = match_date.group(1)
                qso_time_str = match_time.group(1)
                qso_datetime = datetime.strptime(qso_date_str + qso_time_str, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)

                other_locator = match_grid.group(1).strip()
                callsign = match_call.group(1).strip()

                if len(other_locator) < 4: continue
                other_lat, other_lon = common.locator_to_latlon(other_locator)
                if other_lat is None: continue

                distance_km = common.haversine_distance(my_loc_lat, my_loc_lon, other_lat, other_lon)

                # 1. Filtrer uniquement le DX longue distance
                if distance_km < MIN_DX_DISTANCE_KM: continue
                total_dx_contacts += 1

                # 2. Calculer le lever/coucher du soleil pour les deux stations

                # Heures du soleil pour la station locale
                sun_info_my = sun.sun(my_location.observer, date=qso_datetime.date(), tzinfo=timezone.utc)

                # Heures du soleil pour la station distante
                other_location = LocationInfo("DX Station", other_locator, "UTC", other_lat, other_lon)
                sun_info_other = sun.sun(other_location.observer, date=qso_datetime.date(), tzinfo=timezone.utc)

                # Périodes de Greyline (lever/coucher du soleil pour les deux stations)
                greyline_times = []
                if sun_info_my['sunrise']: greyline_times.append(sun_info_my['sunrise'])
                if sun_info_my['sunset']: greyline_times.append(sun_info_my['sunset'])
                if sun_info_other['sunrise']: greyline_times.append(sun_info_other['sunrise'])
                if sun_info_other['sunset']: greyline_times.append(sun_info_other['sunset'])

                # 3. Vérifier si le QSO est dans la fenêtre Greyline
                is_greyline_qso = False
                for sun_time in greyline_times:
                    if sun_time is None: continue

                    # Définir la fenêtre : [SunTime - 30 min, SunTime + 30 min]
                    start_time = sun_time - timedelta(minutes=GREYLINE_WINDOW_MINUTES)
                    end_time = sun_time + timedelta(minutes=GREYLINE_WINDOW_MINUTES)

                    if start_time <= qso_datetime <= end_time:
                        is_greyline_qso = True
                        break

                if is_greyline_qso:
                    greyline_contacts += 1

        # --- Affichage des Résultats ---
        print("\n--- Analyse de Propagation Greyline (DX > {} km) ---".format(MIN_DX_DISTANCE_KM))
        print(f"Fenêtre Greyline (autour du lever/coucher) : +/- {GREYLINE_WINDOW_MINUTES} minutes (Terre et DX).")
        print(f"Total des contacts DX analysés : {total_dx_contacts}")

        if total_dx_contacts > 0:
            percent_greyline = (greyline_contacts / total_dx_contacts) * 100
            print(f"Contacts effectués dans la fenêtre Greyline : {greyline_contacts}")
            print(f"**Pourcentage de votre DX qui s'est produit sur la Greyline : {percent_greyline:.2f} %**")

        else:
            print("Pas assez de contacts DX (>{}) pour une analyse Greyline significative.".format(MIN_DX_DISTANCE_KM))

    except ImportError:
        print("\nERREUR: La librairie 'astral' est nécessaire. Veuillez l'installer avec : pip install astral")
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {file_path} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'analyse: {e}")

# --- Exécution ---
if __name__ == "__main__":
    args = common.get_args("Analyse de Propagation Greyline (DX > {} km)".format(MIN_DX_DISTANCE_KM))
    analyze_greyline(args.file, args.locator)
