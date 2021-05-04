#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import collections
import argparse
import xlwt
import sfi

def main(): 
    # read locus2LG
    LGs1, map1 = read_locus2LG(args.map1)

    # read blast
    blast = read_blast(args.blast)

    name1 = 'sn2'
    name2 = 'Oeu'

    # check
    best12, best21 = check(map1, LGs1, blast, name1, name2)

    # cmp
    cmp_best(best12, best21, name1, name2)
    cmp_best(best21, best12, name2, name1)

def cmp_best(best12, best21, name1, name2):
    # compare reciprocal best pairs of (LG_in_map1, chrom_in_map2) and (LG_in_map2, chrom_in_map1)

    sep = "=" * 20
    print("{} compare {} [{} LGs] vs {} [{} LGs] {}".format(sep, name1, len(best12), name2, len(best21), sep))

    n_OK = 0
    n_KO = 0
    alert = list()
    best = dict()
    for i in best12:
        j = best12[i]
        if j not in best21:
            n_KO += 1
            msg = "* {}:LG{}  => {}:NO_LG".format(name1, i, name2)
            alert.append(msg.replace('* ', ''))
        else:
            k = best21[j] 
            if k == i:
                n_OK += 1
                msg = "  {}:LG{} <=> {}:LG{}".format(name1, i, name2, j)
            else:
                if k == '-':
                    msg = "* {}:LG{}  => {}:LG{} => {}:NO_LG".format(name1, i, name2, j, name1)
                else:
                    msg = "* {}:LG{}  => {}:LG{} => {}:LG{}".format(name1, i, name2, j, name1, k)
                n_KO += 1
                alert.append(msg.replace('* ', ''))
        print(msg)
    print('-' * 20)
    print("summary compare {} [{} LGs] vs {} [{} LGs]\t{} / {} OK\t{} KO\t{}".format(name1, len(best12), name2, len(best21), n_OK, len(best12), n_KO, alert))

def check(map1, LGs1, blast, name1, name2):
    # for each locus in map1, use blast results to collect hit and the corresponding chrom
    # count pairs (LG_in_map1, chrom_in_map2) in count[12]
    # and   pairs (LG_in_map2, chrom_in_map1) in count[21]
    # then for each LG_on_map1 identify the best corresponding chrom_on_map2 as the one with max count
    # and for each chrom_on_map2, identify the best corresponding LG_on_map1 as the one with max count
    # return thses bests results
    
    summary = collections.Counter()
    counts12 = dict()
    counts21 = dict()

    LGs2 = set(blast.values())
    map2 = ()

    for LG1 in LGs1:
        counts12[LG1] = collections.Counter()

    for locus1 in map1:
        summary['mk_in_map1'] += 1
        if locus1 in blast:
            summary['mk_in_map1_with_hit_on_map2'] += 1
            chrom = blast[locus1]
            if chrom not in counts21: 
                counts21[chrom] = collections.Counter()
            for i in map1[locus1]:
                counts12[i][chrom] += 1
                counts21[chrom][i] += 1
                if locus1 in args.trace_loci or chrom in args.trace_LG or args.trace_chrom:
                    print("** check : locus {}, LG{}, chrom {}".format(locus1, i, chrom))

    sep = "=" * 20
    print("{} check {} [{} LGs {:,} mks] vs {} [{} LGs {:,} mks] {}".format(sep, name1, len(LGs1), len(map1), name2, len(LGs2), len(map2), sep))
    pct = float(summary['mk_in_map1_with_hit_on_map2']) /  summary['mk_in_map1'] * 100
    print("{:,} / {:,} ({:.2f}%) mks in {} with hit on {}".format(summary['mk_in_map1_with_hit_on_map2'], summary['mk_in_map1'], pct, name1, name2))
    print('-' * 20)
    best12 = check1(counts12, name1, name2, LGs1)

    print("{} check {} [{} LGs {:,} mks] vs {} [{} LGs {:,} mks] {}".format(sep, name2, len(LGs2), len(map2), name1, len(LGs1), len(map1), sep))
    best21 = check1(counts21, name2, name1, LGs2)
    return best12, best21

def check1(counts, name1, name2, LGs1):

    # check LG from first map with < 0.8 mk on a same LG in map2
    alerts = list()
    best = dict()

    for LG1 in sorted(counts):
        if name1 == 'Oeu':
            str_LG1 = "chr{}".format(LG1)
        else:
            str_LG1 = "LG{}".format(LG1)

        n_tot = sum(counts[LG1].values())
        if n_tot == 0:
            alert = "*"
            alerts.append("{} 0 mk".format(str_LG1))
            print("{} {} 0 / {} mks".format(alert, str_LG1, n_tot))
            continue

        if n_tot < 10:
            alert = "*"
            alerts.append("{} < 10 mks".format(str_LG1))
            print("{} {}:{} {} mks < 10".format(alert, name1, str_LG1, n_tot))
            continue

        list1 = counts[LG1].most_common(5)
        #print(list1)
        LG_best1, n_best1 = list1[0]
        LG_best2, n_best2 = list1[1]
        if name2 == 'Oeu':
            prefix = 'chr'
        else:
            prefix = 'LG'
        str_LG_best1 = "{}{}".format(prefix, LG_best1)
        str_LG_best2 = "{}{}".format(prefix, LG_best2)
        pct_best1 = float(n_best1) / n_tot * 100
        pct_best2 = float(n_best2) / n_tot * 100
        if pct_best1 < 40:
            best[LG1] = '-'
            alert = "*"
            alerts.append("{}:{} bests [{} {:.0f}%, {} {:.0f}%]".format(name1, str_LG1, str_LG_best1, pct_best1, str_LG_best2, pct_best2))
        else:
            best[LG1] = LG_best1
            alert = " "

        #list2 = ["{} on {}".format(n, LG) for LG, n in list1]
        list2 = list()
        for LG, n in list1:
            if name2 == "Oeu":
                str_LG = "chr{}".format(LG)
            else:
                str_LG = "LG{}".format(LG)
            
            list2.append("{} ({:.0f}%) on {}:{}".format(n, (float(n) / n_tot * 100), name2, str_LG))

        #print(list2)
        if name1 == 'Oeu':
            print("{} {}:{} {} mks : {}".format(alert, name1, str_LG1, n_tot, ", ".join(list2)))
        else:
            print("{} {}:{} {} / {} mks : {}".format(alert, name1, str_LG1, n_tot, LGs1[LG1], ", ".join(list2)))
    print('-' * 20)
    print("summary check {} vs {}\t{}/{} alerts\t{}".format(name1, name2, len(alerts), len(LGs1), alerts))
    return best

def read_blast(in_file):
    print("read", in_file)
    blast = dict()
    n = 0
    with open(in_file) as f_in:
        for l in f_in:
            if l.startswith('#'):
                continue
            n += 1
            tab = l.strip().split('\t')
            locus = tab[0]
            chrom = tab[4]
            if chrom.startswith('scaffold'):
                continue
            chrom = int(chrom.replace('chr', ''))
            blast[locus] = chrom
            if locus in args.trace_loci or chrom in args.trace_chrom :
                print("** read_blast : LOCUS={}, CHROM={}".format(locus, chrom))
    print("{:,} loci from blast file {} ".format(n, in_file))
    return blast

def read_locus2LG(in_file):
    print("read", in_file)
    locus2LG = collections.defaultdict(list)
    LGs = collections.defaultdict(int)
    count = collections.defaultdict(int)
    with open(in_file) as f_in:
        for l in f_in:
            count['loci'] += 1
            # unmapped locus => skip
            if l.endswith('\t\n'):
                count['unmapped'] += 1
                continue
            locus, LG = l.strip().split('\t')
            # locus mapped on more than one LG => skip
            if ',' in LG:
                count['mapped_KO'] += 1
                for i in LG.split(','):
                    i = int(i.replace('LG', ''))
                    LGs[i] += 1
                    locus2LG[locus].append(i)
                continue
            LG = int(LG.replace('LG', ''))
            # locus mapped
            count['mapped_OK'] += 1
            LGs[LG] += 1
            locus2LG[locus].append(LG)
            if locus in args.trace_loci or LG in args.trace_LG:
                print("** read_locus2LG : LOCUS={}, LG={}".format(locus, LG))
    for k in ('unmapped', 'mapped_KO', 'mapped_OK'):
        count['pct_{}'.format(k)] = float(count[k]) / count['loci'] * 100
    print("{:,} loci : {:,} ({:.2f}%) unmapped, {:,} ({:.2f}%) bad mapped, {:,} ({:.2f}%) well mapped on {} LGs, from map file {} ".format(count['loci'], count['unmapped'], count['pct_unmapped'], count['mapped_KO'], count['pct_mapped_KO'], count['mapped_OK'], count['pct_mapped_OK'], len(LGs), in_file))
    return LGs, locus2LG

if __name__ == '__main__':
    description = """ 
    compare one map with an assembly (ie a fasta file)
    input : gmap, blast_ok

    input files formats :

    - map
    mk          LG

    - blast_ok
    #qseqid	qlen	qstart	qend	sseqid	slen	sstart	send	length	pident	evalue	score	sstrand
    test1_100017	236	1	142	mse_99192	142	1	142	142	100.000	2.37e-71	142	plus

    output example : LG1 200 mk, 100 (50%) in asm, on 3 LGs : 90 LG1, 5 LG2, 5 LG3
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--map1", help="input file for first map : locus2LG", required=True)
    parser.add_argument("--blast", help="input blast result from first map mk on assembly", required=True)
    parser.add_argument("--trace_loci", nargs="+", help="list of loci to trace", default=[])
    parser.add_argument("--trace_loci_file", help="file list of loci to trace", default="")
    parser.add_argument("--trace_LG", nargs="+", help="list of LG to trace", default=[])
    parser.add_argument("--trace_chrom", nargs="+", help="list of chrom to trace", default=[])

    args = parser.parse_args()
    if args.trace_loci_file != "":
        args.trace_loci = sfi.file2list(args.trace_loci_file)
        print("{} loci to trace from file {}".format(len(args.trace_loci), args.trace_loci_file))
    main() 
