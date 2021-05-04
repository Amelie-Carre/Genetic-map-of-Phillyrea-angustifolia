#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import collections

def main(): 

    skip_LG = set(args.skip_LG)

    positions = dict()
    # reads in_map, and collect positions
    if args.verbose: print("read {}".format(args.in_map))
    with open(args.in_map) as f_in:
        n = 0
        for l in f_in:
            if l.startswith('#') or l.startswith('MARKER'):
                f_out.write(l)
            else:
                snp, LG, pos1, pos2 = l.strip().split(',')
                if LG in skip_LG:
                    continue
                locus = snp2locus(snp)
                if locus not in positions:
                    positions[locus] = collections.Counter()
                key = (LG, pos1, pos2)
                positions[locus][key] += 1
                n += 1
    print("{:,} snps, {:,} loci from {}".format(n, len(positions), args.in_map))

    distrib = collections.defaultdict(int)
    for locus in positions:
        distrib[len(positions[locus])] += 1

    print("number of locus per snp in locus: {}".format(", ".join(["{:,}:{}".format(distrib[i], i) for i in sorted(distrib)])))

    if args.verbose: print("write {}".format(args.out_map))
    with open(args.out_map, "w") as f_map:
        n = 0
        status = collections.defaultdict(int)
        for locus in positions:
            keys = list(positions[locus].keys())
            if len(keys) == 1:
                key = keys[0]
                # print("locus uniq pos", key)
                f_map.write("{},{},{},{}\n".format(locus, *key))
                status['OK_uniq_pos'] += 1
                n += 1
            else:
                #print("locus", positions[locus])
                # collect all LG
                LGs = set()
                for key in positions[locus]:
                    LG = key[0]
                    #print("key {} LG {}".format(key, LG))
                    LGs.add(LG)
                #print("all LGs", LGs)
                if len(LGs) > 1:
                    print("skip locus {} : more than one LG {}".format(locus, sorted(list(LGs))))
                    status['KO_multi_LG'] += 1
                else:
                    key = positions[locus].most_common()[0][0]
                    #print("most common on same LG {} : {}".format(LG, key))
                    f_map.write("{},{},{},{}\n".format(locus, *key))
                    status['OK_multi_pos_same_LG'] += 1
                    n += 1

    print("number of locus per status: {}".format(", ".join(["{:,}:{}".format(status[i], i) for i in sorted(status)])))
    print("{:} mk written to {}".format(n, args.out_map))

def snp2locus(snp):
    locus = "_".join(snp.split('_')[:-1])
    return locus

if __name__ == '__main__':
    description = """ convert lepmap3 final map from snps position to loci positions
    orig gmap = snp, LG, Male_pos, Female_pos  (snp = locus name + snp position in locus)
    exemple sn2_26069_142bp_108,20,2.965,10.087
    skip LG 20
    if one locus > 1 snp with différent map position :
    => warning + use position with max snps
    if same number (eg 1 snp mapped at 5 cM and 1 snp mapped at 8 cM), use min position (5 cM in this example)

    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--in_map", help="input lepmap3 final map, after orderMarker", required=True)
    parser.add_argument("--out_map", help="output new map", required=True)
    parser.add_argument("--skip_LG", nargs="+", help="skip these LG", default = [])

    args = parser.parse_args()

    main() 
