#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import argparse

def main():
    for map_file in args.maps:
        stat_map(map_file)

def stat_map(map_file):
    # read map map, collect line number to keep
    count = collections.defaultdict(int)
    LGs = set()
    with open(map_file) as f_map:
        n = 0
        for l in f_map:
            if l.startswith('#'):
                continue
            n += 1
            count['tot_mk'] += 1
            LG = int(l.strip().split('\t')[0])
            if LG == 0:
                count['single'] += 1
            else:
                count[LG] += 1
                LGs.add(LG)
                count['mapped_mk'] += 1
                if n < 8 :
                    count['mapped_pheno'] += 1

    count['LGs'] = len(list(LGs))

    if count['LGs'] > 0:
        mean_mk_per_LG = int(count['mapped_mk'] / count['LGs'])
    else:
        mean_mk_per_LG = 0

    if args.info_mk == 0:
        if count['tot_mk'] == 0:
            return
        else: 
            pct_mapped = float(count['mapped_mk']) / count['tot_mk'] * 100
    else:
        pct_mapped = float(count['mapped_mk']) / args.info_mk * 100
    print("{:25s} : {} LGs, {} pheno mapped, {:,} mk mapped ({:.2f}%), ~ {:,} mk per LG, {:,} mk single, {:,} tot mk".format(map_file, count['LGs'], count['mapped_pheno'], count['mapped_mk'], pct_mapped, mean_mk_per_LG, count['single'], count['tot_mk']))
    #for LG in sorted(list(LGs)):
    #    print("LG {:,} : {:,} mk".format(LG, count[LG]))

if __name__ == '__main__':
    description = """ stats on lepmap3 map """

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--maps", nargs="+", help="input map form SeparateChromosome", required=True)
    parser.add_argument("--info_mk", type=int, help="number of informative markers", default=0)

    args = parser.parse_args()
    main() 
