#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import collections

def main(): 
    l_min, l_max, l_step = args.lod.split(':')
    s_min, s_max, s_step = args.size.split(':')

    l_options = range(int(l_min), int(l_max) + 1, int(l_step))
    s_options = range(int(s_min), int(s_max) + 1, int(s_step))

    suffix='rsrcsrc'
    sd_select = read_list('sd_select')
    print("lod\tsize\tsd_found/sd_total\tsd_LGS\tLGs\tpct snp mapped\tsnp mapped\tsnp total\tLG details")
    for lod in l_options:
        for size in s_options:
            map_file = 'sn2/tests/map_l_{lod}_s_{size}{suffix}.txt'.format(lod=lod, size=size, suffix=suffix)
            locus_file = 'sn2/tests/metrics/map_l_{lod}_s_{size}{suffix}/map_l_{lod}_s_{size}{suffix}_locus2LG.txt'.format(lod=lod, size=size, suffix=suffix)
            read_result(lod, size, map_file, locus_file, sd_select)

def read_result(lod, size, map_file, locus_file, sd_select):
    count = collections.defaultdict(int)
    mapped = 0
    total = 0
    sd_select_ok = 0
    with open(map_file) as f_in:
        for l in f_in:
            if l.startswith("#"):
                continue
            LG = int(l.strip())
            count[LG] += 1
            total += 1
            if LG != 0:
                mapped += 1
    pct_mapped = mapped / total * 100
    details = ", ".join(["LG{}={}".format(LG, count[LG]) for LG in sorted(count)])

    sd_LGS = collections.defaultdict(list)
    with open(locus_file) as f_in:
        for l in f_in:
            #print(l)
            tab = l.strip().split('\t')
            if len(tab) < 2:
                continue
            locus, LG = l.strip().split('\t')
            if locus in sd_select:
                sd_select_ok += 1
                sd_LGS[LG].append(locus)

    n_select = len(sd_select)
    sd_details = ", ".join(["LG{}={}".format(LG, sd_LGS[LG]) for LG in sorted(sd_LGS)])
    print("{lod}\t{size}\t{sd_select_ok}/{n_select}\t{sd_LGS}\t{lgs}\t{pct_mapped}\t{mapped}\t{total}\t{details}".format(lod=lod, size=size, lgs=len(count) - 1, pct_mapped=pct_mapped, mapped=mapped, total=total, details=details, sd_select_ok=sd_select_ok, n_select=n_select, sd_LGS=sd_details))

def read_list(in_file):
    select = set()
    with open(in_file) as f_in:
        for l in f_in:
            select.add(l.strip())
    return select

if __name__ == '__main__':
    description = """ summary mapping results """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--name", help="sn2, sn3")
    parser.add_argument("--lod", help="lodscore min:max:step")
    parser.add_argument("--size", help="LG size min:max:step")

    args = parser.parse_args()
    main() 
