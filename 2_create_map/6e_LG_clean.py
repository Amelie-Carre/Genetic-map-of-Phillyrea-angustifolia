#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from Bio import SeqIO
import sfi

def main(): 

    line2snp = dict()
    bad_loci = dict()

    # reads loci2LG file to collect bad loci names [loci_name LG_list], ie loci with at least 2 LG
    if args.verbose: print("read", args.loci2LG)
    with open(args.loci2LG) as f_in:
        n = 0
        for l in f_in:
            n += 1
            # do not use strip, since it will strip \t if second column is empty
            locus, LGs = l.split('\t')
            if ',' in LGs:
                bad_loci[locus] = LGs.strip()
    print("{}/{} bad loci from {}".format(len(bad_loci), n, args.loci2LG))

    # reads snp_name file [nb_line seq_name pos] to get association between line number and snp name
    if args.verbose: print("read", args.snp_name)
    with open(args.snp_name) as f_in:
        n = 0
        for l in f_in:
            n += 1
            n_line, locus, pos = l.strip().split('\t')
            n_line = int(n_line)
            line2snp[n_line] = (locus, pos)
            #print("line {} => locus {}".format(n_line, locus))
    print("{} lines from {}".format(n, args.snp_name))

    # reads in_map, reset snp for bad_mapped loci and write out_map
    if args.verbose: print("read {}, write {}".format(args.in_map, args.out_map))
    with open(args.in_map) as f_in, open(args.out_map, 'w') as f_out:
        n = 0
        total_snps = 0
        cleaned_snps = 0
        total_loci = set()
        cleaned_loci = set()
        for l in f_in:
            tab = l.strip().split('\t')
            if l.startswith('#'):
                f_out.write(l)
            else:
                n += 1
                total_snps += 1
                locus, pos = line2snp[n]
                total_loci.add(locus)

                if locus in bad_loci:
                    f_out.write("0\n")
                    cleaned_snps += 1
                    cleaned_loci.add(locus)
                    print("clean n={}, locus={}, pos={}, LGs={}".format(n, locus, pos, bad_loci[locus]))
                else:
                    f_out.write(l)

    print("{}/{} cleaned_snp, {}/{} cleand_loci from {}".format(cleaned_snps, total_snps, len(cleaned_loci), len(total_loci), args.in_map))

if __name__ == '__main__':
    description = """ 
    clean lepmap3 intermediate map to remove bad_mapped loci
    a bad locus is a locus with at least 2 snps mapped in 2 différent LG
    reset LG for all snps of these bad loci
    reset = set LG to 0, that means that this snp is not affected to any LG
    reads loci2LG file to collect bad loci names [loci_name LG_list], ie loci with at least 2 LG
    reads recode file [nb_line seq_name pos] to get association between line number and snp name
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--in_map", help="input lepmap3 final map, after orderMarker", required=True)
    parser.add_argument("--out_map", help="output new map", required=True)
    parser.add_argument("--loci2LG", help="input file used to collect bad_mapped loci loci [loci_name LG_list]", required=True)
    parser.add_argument("--snp_name", help="input file for recoding [nb_line seq_name pos]", required=True)

    args = parser.parse_args()

    main() 
