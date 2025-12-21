"""Module to calculate antipode, antecoique, periecoique from adif file"""
import re
import common # Utilise ton fichier common.py existant

def find_closest_points(adif_records, my_loc):
    """Closest contact from adif file for antipode, antecoique, periecoique"""
    lat, lon = common.locator_to_latlon(my_loc)

    # Définition des 3 points cibles
    targets = {
        "Antipode": (-1 * lat, (lon + 180 + 180) % 360 - 180),
        "Antécoïque": (-1 * lat, lon),
        "Périécoïque": (lat, (lon + 180 + 180) % 360 - 180)
    }

    results = {k: {"dist": float('inf'), "call": None} for k in targets}
    re_grid = re.compile(r'(?i)<GRIDSQUARE:\d+>([A-Z]{2}\d{2})')
    re_call = re.compile(r'(?i)<CALL:\d+>([^>]+)')

    for record in adif_records:
        m_grid = re_grid.search(record)
        m_call = re_call.search(record)
        if m_grid and m_call:
            c_lat, c_lon = common.locator_to_latlon(m_grid.group(1))
            if c_lat is None:
                continue

            for name, coords in targets.items():
                d = common.haversine_distance(c_lat, c_lon, coords[0], coords[1])
                if d < results[name]["dist"]:
                    results[name] = {"dist": d, "call": m_call.group(1).split('<')[0]}

    print(f"--- Records de proximité pour {my_loc} ---")
    for name, data in results.items():
        print(f"{name:<12}: {data['call'] or 'Aucun':<10} à {data['dist']:7.1f} km du point idéal")

if __name__ == "__main__":
    args = common.get_args()
    with open(args.file, "r", encoding="ascii") as f:
        records = re.split(r'(?i)<EOR>', f.read())
    find_closest_points(records, args.locator)
