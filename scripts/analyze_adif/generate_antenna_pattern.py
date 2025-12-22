'''Module create compass rose in ascii from adif file.'''
import re
import math
import common

def calculate_initial_bearing(lat1, lon1, lat2, lon2):
    '''calculate_initial_bearing function'''
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def draw_star_radar(adif_records, my_locator, radius=12):
    '''Draw star radar function'''
    my_lat, my_lon = common.locator_to_latlon(my_locator)
    sectors = [0] * 16
    re_grid = re.compile(r'(?i)<GRIDSQUARE:\d+>([A-Z]{2}\d{2})')

    for record in adif_records:
        match = re_grid.search(record)
        if match and (other := common.locator_to_latlon(match.group(1))):
            if other[0] is not None:
                brng = calculate_initial_bearing(my_lat, my_lon, other[0], other[1])
                sectors[int(((brng + 11.25) % 360) / 22.5) % 16] += 1

    max_val = max(sectors) if max(sectors) > 0 else 1
    size = radius * 2 + 3
    grid = [[" " for _ in range(size)] for _ in range(size)]
    center = radius + 1

    # 1. Dessiner les lignes de structure (la rosace vide)
    for r in range(1, radius + 1):
        for i in range(8): # 8 directions principales
            angle = math.radians(i * 45 - 90)
            grid[int(center + r * math.sin(angle))][int(center + r * math.cos(angle))] = "·"

    # 2. Superposer les données de trafic (caractères denses)
    chars = [".", "o", "0", "#"]
    for i in range(16):
        angle = math.radians(i * 22.5 - 90)
        len_line = int((sectors[i] / max_val) * radius)
        idx_char = min(len(chars)-1, int((sectors[i] / max_val) * len(chars)))
        char = chars[idx_char]
        for r in range(1, len_line + 1):
            grid[int(center + r * math.sin(angle))][int(center + r * math.cos(angle))] = char

    # 3. Ajouter les étiquettes et le centre
    grid[0][center] = "N"
    grid[size-1][center] = "S"
    grid[center][size-1] = "E"
    grid[center][0] = "W"
    grid[center][center] = "*"

    # Affichage
    print(f"\n--- ROSACE DE RÉCEPTION (Contacts: {sum(sectors)}) ---")
    for row in grid:
        print(" ".join(row))
    print("\nLégende: · = Axe vide | # = Trafic dense | * = ", my_locator)
    print("")

if __name__ == "__main__":
    args = common.get_args()
    with open(args.file, "r", encoding="ascii") as f:
        records = re.split(r'(?i)<EOR>', f.read())
    draw_star_radar(records, args.locator)
