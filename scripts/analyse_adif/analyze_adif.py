#!/usr/bin/env python3
"""
Analyse les fichiers ADIF
"""
import argparse
import sys
import analyze_adif_dx_performance as adx
import analyze_adif_schedule as ads
import analyze_snr_performance as asp
import find_top_dx_contacts as ftdx
import analyze_adif_mode as adm
import analyze_weekly_traffic as awt
import common

def main(records, args):
    adx.analyze_dx_performance(records, args.locator)
    ads.analyze_adif_log(records)
    asp.analyze_snr(records)
    ftdx.find_top_dx(records, args.locator, cty_dat_path=args.ctydat)
    adm.analyze_adif_modes(records)
    awt.analyze_weekly_traffic(records)

if __name__ == "__main__":
    args = common.get_args()
    try:
        records = common.read_file_content(args.file)
        main(records, args)
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {args.file} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution: {e}")
