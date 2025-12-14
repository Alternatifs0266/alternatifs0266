""" Module commun. """
import math
import argparse

# --- Configuration ---
ADIF_FILE_PATH = 'f4lno.adif'
# VEUILLEZ RENSEIGNER VOTRE PROPRE LOCALISATEUR QRA (ex: 'JN33')
MY_LOCATOR = 'JN33' # <--- REMPLACEZ PAR VOTRE VRAI LOCALISATEUR QRA

def locator_to_latlon(locator):
    """Convertit un localisateur QRA (4 ou 6 chars) en (Latitude, Longitude)"""
    locator = locator.upper().strip()
    if len(locator) < 4:
        return None, None

    lon = (ord(locator[0]) - ord('A')) * 20 - 180
    lat = (ord(locator[1]) - ord('A')) * 10 - 90
    lon += (int(locator[2])) * 2
    lat += (int(locator[3])) * 1

    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord('A')) * (2/24) + (1/24)
        lat += (ord(locator[5]) - ord('A')) * (1/24) + (0.5/24)
    elif len(locator) == 4:
        lon += 1.0
        lat += 0.5

    return lat, lon


def latlon_to_locator(lat, lon, precision=4):
    """
    Convert latitude/longitude to Maidenhead locator.

    Args:
    lat (float): Latitude in degrees (-90 to 90).
    lon (float): Longitude in degrees (-180 to 180).
    precision (int): 2 for 2-char (field), 4 for 4-char (square), 6 for 6-char (subsquare), etc.

    Returns:
    str: Maidenhead locator string.
    """
    # Adjust to 0-360 range for lon, 0-180 for lat
    lat += 90
    lon += 180

    locator = ''

    # Field level (20° lon x 10° lat, A-R / 0-9)
    field_lat = int(lat / 10)
    field_lon = int(lon / 20)
    locator += chr(ord('A') + field_lon)
    locator += chr(ord('A') + field_lat)
    locator += str(int(int(lon) % 20 / 2))
    locator += str(int(int(lat) % 10 / 1))

    if precision <= 4:
        return locator

    # Subsquare level (2° lon x 1° lat, a-x / 0-9)
    lat_rem = lat % 1
    lon_rem = lon % 2
    sub_lat = int(lat_rem * 10)
    sub_lon = int(lon_rem * 10)
    locator += chr(ord('a') + sub_lon)
    locator += chr(ord('a') + sub_lat)

    return locator[:precision]


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux points Lat/Lon (Formule Haversine)"""
    r = 6371  # Rayon de la Terre en kilomètres
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = r * c
    return distance


# Mapping des fréquences (en MHz) vers les bandes amateur
def get_band_from_frequency(freq_mhz):
    """ Mappe une fréquence en MHz à une bande amateur """
    if 1.8 <= freq_mhz < 2:
        return '160m'
    if 3.5 <= freq_mhz < 4:
        return '80m'
    if 7 <= freq_mhz < 8:
        return '40m'
    if 10 <= freq_mhz < 11:
        return '30m'
    if 14 <= freq_mhz < 15:
        return '20m'
    if 18 <= freq_mhz < 19:
        return '17m'
    if 21 <= freq_mhz < 22:
        return '15m'
    if 24 <= freq_mhz < 25:
        return '12m'
    if 28 <= freq_mhz < 30:
        return '10m'
    if 50 <= freq_mhz < 54:
        return '6m'
    if 70 <= freq_mhz < 72:
        return '4m'
    if 144 <= freq_mhz < 148:
        return '2m'
    if 430 <= freq_mhz < 440:
        return '70cm'
    return 'Autres'  # Regrouper les fréquences non standard


def get_args(description="Analyze ADIF files"):
    """Analyse les arguments de la ligne de commande"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-f', '--file', help=f"Chemin vers le fichier ADIF (defaut: {ADIF_FILE_PATH})", default=ADIF_FILE_PATH)
    parser.add_argument('-l', '--locator', help=f"Votre localisateur QRA (defaut: {MY_LOCATOR})", default=MY_LOCATOR)
    parser.add_argument('-c', '--ctydat', help="Chemin vers le fichier cty.dat pour les pays DXCC (https://www.country-files.com/)", default="cty.dat")
    args = parser.parse_args()

    args.locator = args.locator.upper()

    print(f"Analyse de {args.file} avec le localisateur {args.locator}")
    return args

def read_file_content(file_path):
    """Lit le contenu d'un fichier ADIF et retourne les enregistrements."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().upper()
        records = content.split('<EOR>')
    return records
