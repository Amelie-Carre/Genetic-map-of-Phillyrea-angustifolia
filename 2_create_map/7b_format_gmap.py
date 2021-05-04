#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from Bio import SeqIO
import sfi

def main(): 

    Oeu_LGS = [i for i in range(1,24)]
    Pan_LGS = [i for i in range(1,23)] + [24, ]

    # reads renum_LG file
    LG_Oeu2Pan = reads_Pan_2_Oeu(args.renum_LG, Oeu_LGS, Pan_LGS)

    # reads recode_mk file
    snp_num2ID = read_recode_mk(args.recode_mk)

    # reads all results from + recode LG ans recode markers
    gmap = dict()
    tot_mk = 0
    tot_cM1 = 0
    tot_cM2 = 0

    for Oeu_LG in Oeu_LGS:
        Pan_LG = LG_Oeu2Pan[Oeu_LG]
        in_map_file = "{}_{}_{}.txt".format(args.in_basename, Pan_LG, args.in_sex)
        n_mk, cM1, cM2 = read_lepmapOM(gmap, in_map_file, Pan_LG, Oeu_LG, snp_num2ID)
        tot_mk += n_mk
        tot_cM1 += cM1
        tot_cM2 += cM2
    print("{} mk written to {}, total {}, {} CM".format(tot_mk, args.out_map, tot_cM1, tot_cM2))

    # write map
    write_map(args.out_map, Oeu_LGS, gmap)

def reads_Pan_2_Oeu(renum_LG, Oeu_LGS, Pan_LGS):
    Pan2Oeu = dict()
    Oeu2Pan = dict()

    # reads renum_file
    if args.verbose: print("read", renum_LG)
    with open(renum_LG) as f_in:
        for l in f_in:
            if l.startswith('#'):
                continue
            Pan_LG, Oeu_chrom = l.strip('\n').split(':')
            Pan_LG = int(Pan_LG)
            Oeu_chrom = int(Oeu_chrom)
            if Pan_LG in Pan2Oeu:
                print("Erreur : Pan LG {} already associated to Oeu chrom {}, skip second associattion to new Oeu chrom {}".format(Pan_LG, Pan2Oeu[Pan_LG], Oeu_chrom))
                errors += 1
            else:
                Pan2Oeu[Pan_LG] = Oeu_chrom
            if Oeu_chrom in Oeu2Pan:
                print("Erreur : Oeu chrom {} already associated to Pan LG {}, skip second associattion to new Pan LG {}".format(Oeu_chrom, Oeu2Pan[Oeu_chrom], Pan_LG))
                errors += 1
            else:
                Oeu2Pan[Oeu_chrom] = Pan_LG
    # check
    errors = 0

    if len(Pan2Oeu) != 24:
        print("Erreur : {} Pan LG, should be 23".format(len(Pan2Oeu)))
        errors += 1
    if len(Oeu2Pan) != 24:
        print("Erreur : {} Oeu chrom, should be 23".format(len(Oeu2Pan)))
        errors += 1

    for Pan_LG in Pan_LGS:
        if Pan_LG not in Pan2Oeu:
            print("Pan_LG {} unknown in renum file {}".format(Pan_LG, renum_LG))
            errors += 1

    for Oeu_LG in Oeu_LGS:
        if Oeu_LG not in Oeu2Pan:
            print("Oeu_LG {} unknown in renum file {}".format(Oeu_LG, renum_LG))
            errors += 1

    if errors > 0:
        print("{} errors, exit".format(errors))
        exit(1)

    return Oeu2Pan

def read_recode_mk(recode_mk):
    l2mk = dict()

    if args.verbose: print("read", recode_mk)
    with open(recode_mk) as f_in:
        n_line = 0
        for l in f_in:
            n_line, seq, pos = l.strip().split('\t')
            n_line = n_line
            mk_id = "{}_{}".format(seq, pos)
            l2mk[n_line] = mk_id
            # print("line {} => mk_id {}".format(n_line, mk_id))
    return l2mk

def read_lepmapOM(gmap, in_map_file, Pan_LG, Oeu_chrom, snp_num2ID):

    # reads in_map, recode markers and LG, then store map
    #if args.verbose: print("read {}".format(in_map_file))
    gmap[Oeu_chrom] = list()
    n_mk = 0
    pos1 = 0
    pos2 = 0
    with open(in_map_file) as f_in:
        for l in f_in:
            if l.startswith('#'):
                continue
            tab = l.strip().split('\t')
            mk = tab[0]
            new_mk = snp_num2ID[mk]
            pos1 = float(tab[1])
            pos2 = float(tab[2])
            gmap[Oeu_chrom].append([new_mk, Oeu_chrom, pos1, pos2])
        if args.verbose: 
            print("Oeu_chrom {} [Pan_LG {}]: {} markers, {}/{} cM".format(Oeu_chrom, Pan_LG, len(gmap[Oeu_chrom]), pos1, pos2))
    return (len(gmap[Oeu_chrom]), pos1, pos2)

def write_map(out_map, Oeu_LGS, gmap):
    with open(args.out_map, 'w') as f_out:
        for Oeu_LG in Oeu_LGS:
            for mk, LG, pos1, pos2 in gmap[int(Oeu_LG)]:
                f_out.write("{},{},{},{}\n".format(mk, Oeu_LG, pos1, pos2))


if __name__ == '__main__':
    description = """
    creates gmap format from lepmap3 results
    - concat result from order markers for all LG, using args basename
    - rename LG from Oeu chromosomes, using arg file renum_LG
    - rename markers from marker number to locus name + pos in locus, using args file recode_snp
    - output map to args out_map

    File formats : 
    renum_LG [input] :
    Pan_LG:Oeu_chrom
    
    recode_snp [input] : 
    num	locus_name	pos
    4	sn2_15_143bp	140

    lepmap3 order markers result [input] :
    #marker_number	male_position	female_position	( 0.0 )[	phased data]
    # if sex option == 1, male_pos = female_pos = average_pos
    
    gmap [output] : 
    mk_name,LG,pos1,pos2   (LG=int, pos1 and pos2=float for cM position)

"""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--in_basename", help="basename for each LG result from lepmap3 OrderMarker", required=True)
    parser.add_argument("--in_sex", type=int, choices=[0, 1], help="sex option [0, 1]", required=True)
    parser.add_argument("--renum_LG", help="txt file for renaming LG based on Oeu chrom", required=True)
    parser.add_argument("--recode_mk", help="txt file for recoding markers from number to locus+pos", required=True)
    parser.add_argument("--out_map", help="output map (gmap format)", required=True)
    args = parser.parse_args()

    main() 
