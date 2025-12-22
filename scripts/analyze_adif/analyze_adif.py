#!/usr/bin/env python3
"""
Analyse les fichiers ADIF
"""
import adif_to_ascii_map as aam
import analyze_adif_dx_performance as adx
import analyze_adif_schedule as ads
import analyze_snr_performance as asp
import find_top_dx_contacts as ftdx
import analyze_adif_mode as adm
import analyze_greyline_dx as agd
import analyze_weekly_traffic as awt
import analyze_by_country as abc
import analyze_antipode as aap
import generate_antenna_pattern as gap
import common

def main(adif_records, adif_file, locator, cty_dat_path=None):
    """ Exécute toutes les analyses ADIF disponibles. """
    aam.tracer_carte(aam.parse_adif_locators(adif_file))
    gap.draw_star_radar(adif_records, locator)
    aap.find_closest_points(adif_records, locator)
    adx.analyze_dx_performance(adif_records, locator)
    awt.analyze_weekly_traffic(adif_records)
    adm.analyze_adif_modes(adif_records)
    ads.analyze_adif_log(adif_records)
    asp.analyze_snr(adif_records)
    abc.analyze_contacts_by_band_country(adif_records, cty_dat_path=cty_dat_path)
    ftdx.find_top_dx(adif_records, locator, cty_dat_path=cty_dat_path)
    agd.analyze_greyline(adif_records, locator)

if __name__ == "__main__":
    args = common.get_args()
    try:
        records = common.read_file_content(args.file)
        main(records, args.file, args.locator, cty_dat_path=args.ctydat)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution: {e}")
