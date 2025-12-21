#!/usr/bin/env python3
"""
Analyse les fichiers ADIF
"""
import analyze_adif_dx_performance as adx
import analyze_adif_schedule as ads
import analyze_snr_performance as asp
import find_top_dx_contacts as ftdx
import analyze_adif_mode as adm
import analyze_greyline_dx as agd
import analyze_weekly_traffic as awt
import analyze_by_country as abc
import common

def main(adif_records, locator, cty_dat_path=None):
    """ Exécute toutes les analyses ADIF disponibles. """
    adx.analyze_dx_performance(adif_records, locator)
    ads.analyze_adif_log(adif_records)
    asp.analyze_snr(adif_records)
    ftdx.find_top_dx(adif_records, locator, cty_dat_path=cty_dat_path)
    adm.analyze_adif_modes(adif_records)
    agd.analyze_greyline(adif_records, locator)
    awt.analyze_weekly_traffic(adif_records)
    abc.analyze_contacts_by_band_country(adif_records, cty_dat_path=cty_dat_path)

if __name__ == "__main__":
    args = common.get_args()
    try:
        records = common.read_file_content(args.file)
        main(records, args.locator, cty_dat_path=args.ctydat)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution: {e}")
