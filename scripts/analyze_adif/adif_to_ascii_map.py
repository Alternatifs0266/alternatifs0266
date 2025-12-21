import re
from collections import defaultdict
import common


# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------
# Dimensions de la carte (largeur x hauteur)
WIDTH = 100
HEIGHT = 30

# ----------------------------------------------------------------------
# 2. FONCTIONS DE CONVERSION
# ----------------------------------------------------------------------

def locator_to_latlon(locator):
    """Convertit un Maidenhead Locator (ex: JN23) en Lat/Lon décimales."""
    locator = locator.upper()
    try:
        # Longitude : les deux premières lettres
        lon = (ord(locator[0]) - ord('A')) * 20 - 180
        # Latitude : les deux lettres suivantes
        lat = (ord(locator[1]) - ord('A')) * 10 - 90
        
        # Ajout des chiffres pour plus de précision (4 caractères)
        if len(locator) >= 4:
            lon += int(locator[2]) * 2
            lat += int(locator[3]) * 1
            
        # On centre au milieu du carreau (0.5 pour la précision)
        return lat + 0.5, lon + 1.0
    except Exception:
        return None

def parse_adif_locators(filepath):
    """Extrait les codes GRIDSQUARE du fichier ADIF."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # On cherche les balises <GRIDSQUARE:4>JN23 par exemple
            return re.findall(r'<GRIDSQUARE:\d+>([A-R]{2}\d{2})', content, re.IGNORECASE)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{filepath}' est introuvable.")
        return []

# ----------------------------------------------------------------------
# 3. GÉNÉRATION DE LA CARTE
# ----------------------------------------------------------------------

def tracer_carte(locators):
    # Initialiser une grille vide
    grid = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # --- DESSINER L'ÉQUATEUR ---
    # L'équateur est à 0° de latitude. 
    # Dans notre grille (90 à -90), le milieu exact est (HEIGHT-1) / 2
    y_equateur = int(((90 - 0) / 180) * (HEIGHT - 1))
    
    for x in range(WIDTH):
        grid[y_equateur][x] = '-'  # Caractère pour l'équateur

    # Ajouter une petite légende sur l'équateur
    label = " EQUATEUR "
    start_pos = (WIDTH // 2) - (len(label) // 2)
    for i, char in enumerate(label):
        grid[y_equateur][start_pos + i] = char

    # --- PLACER LES CONTACTS ---
    points_plottes = 0
    for loc in locators:
        coords = locator_to_latlon(loc)
        if coords:
            lat, lon = coords
            # Projection simple sur la grille
            # X: -180 à 180 -> 0 à WIDTH
            x = int(((lon + 180) / 360) * (WIDTH - 1))
            # Y: 90 à -90 -> 0 à HEIGHT (le haut est 90N)
            y = int(((90 - lat) / 180) * (HEIGHT - 1))
            
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                # 'X' écrase l'équateur si le contact est pile dessus
                grid[y][x] = 'X' 
                points_plottes += 1

    # --- AFFICHAGE FINAL ---
    print("\n" + "=" * WIDTH)
    print(f" CARTE DES CONTACTS ADIF - F4LNO (Total: {len(locators)} contacts)")
    print("=" * WIDTH)
    
    for row in grid:
        print("".join(row))
        
    print("=" * WIDTH)
    print(f"Légende : 'X' = Contact | '-' = Équateur")
    print(f"Nombre de points affichés : {points_plottes}")

# ----------------------------------------------------------------------
# 4. LANCEMENT
# ----------------------------------------------------------------------
if __name__ == "__main__":
    args = common.get_args("Adif to Ascii Map")
    liste_locs = parse_adif_locators(args.file)
    if liste_locs:
        tracer_carte(liste_locs)
