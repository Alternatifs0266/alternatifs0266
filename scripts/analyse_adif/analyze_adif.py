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

def main(args):
    adx.analyze_dx_performance(args.file, args.locator)
    ads.analyze_adif_log(args.file)
    asp.analyze_snr(args.file)
    ftdx.find_top_dx(args.file, args.locator, cty_dat_path=args.ctydat)
    adm.analyze_adif_modes(args.file)
    awt.analyze_weekly_traffic(args.file)

if __name__ == "__main__":
    args = common.get_args()
    main(args)
