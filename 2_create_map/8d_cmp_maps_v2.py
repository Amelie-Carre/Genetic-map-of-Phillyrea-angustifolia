#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import collections
import argparse
import xlwt

def main(): 
    # read second locus2LG
    LGs1, map1 = read_locus2LG(args.map1)

    # read second locus2LG
    LGs2, map2 = read_locus2LG(args.map2)

    # read blast
    blast12, blast21 = read_blast(args.blast)

    name1 = 'sn2'
    name2 = 'MSE'

    # check
    best12 = check(map1, map2, LGs1, LGs2, blast12, name1, name2)
    best21 = check(map2, map1, LGs2, LGs1, blast21, name2, name1)

    # cmp
    cmp_best(best12, best21, name1, name2)
    cmp_best(best21, best12, name2, name1)

def cmp_best(best12, best21, name1, name2):
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

def check(map1, map2, LGs1, LGs2, blast, name1, name2):
    summary = collections.Counter()
    counts = dict()
    best = dict()

    for LG1 in LGs1:
        counts[LG1] = collections.Counter()

    for locus1 in map1:
        LG1 = map1[locus1]
        summary['mk_in_map1'] += 1
        if locus1 in blast:
            summary['mk_in_map1_with_hit_on_map2'] += 1
            locus2 = blast[locus1]
            if locus2 in map2:
                LG2 = map2[locus2]
                #print("{} [{}] => {} [{}]".format(locus1, LG1, locus2, LG2))
                counts[LG1][LG2] += 1
    sep = "=" * 20
    print("{} check {} [{} LGs {:,} mks] vs {} [{} LGs {:,} mks] {}".format(sep, name1, len(LGs1), len(map1), name2, len(LGs2), len(map2), sep))

    print("{:,} / {:,} ({:.2f}%) mks in {} with hit on {}".format(summary['mk_in_map1_with_hit_on_map2'], summary['mk_in_map1'], float(summary['mk_in_map1_with_hit_on_map2']) /  summary['mk_in_map1'] * 100, name1, name2))

    print('-' * 20)

    # check LG from first map with < 0.8 mk on a same LG in map2
    alerts = list()
    for LG1 in sorted(LGs1):
        n_tot = sum(counts[LG1].values())
        if n_tot == 0:
            alert = "*"
            alerts.append("LG{} 0 mk".format(LG1))
            print("{} LG{} 0 / {} mks".format(alert, LG1, n_tot))
            continue
        list1 = counts[LG1].most_common(5)
        #print(list1)
        LG_best, n_best = list1[0]
        pct_best = float(n_best) / n_tot * 100
        if pct_best < 80:
            alert = "*"
            alerts.append("{}:LG{} best {:.0f}%".format(name1, LG1, pct_best))
            best[LG1] = "-"
        else:
            alert = " "
            best[LG1] = LG_best
        list2 = ["{} ({:.0f}%) on {}:LG{}".format(n, (float(n) / n_tot * 100), name2, LG) for LG, n in list1]
        #print(list2)
        print("{} {}:LG{} {} / {} mks : {}".format(alert, name1, LG1, n_tot, LGs1[LG1], ", ".join(list2)))
    print('-' * 20)
    print("summary check {} [{} LGs {:,} mks] vs {} [{} LGs {:,} mks]\t{}/{} alerts\t{}".format(name1, len(LGs1), len(map1), name2, len(LGs2), len(map2), len(alerts), len(LGs1), alerts))
    return best

def read_blast(in_file):
    print("read", in_file)
    blast12 = dict()
    blast21 = dict()
    n = 0
    with open(in_file) as f_in:
        for l in f_in:
            if l.startswith('#'):
                continue
            n += 1
            tab = l.strip().split('\t')
            mk1 = tab[0].replace('test1_', '')
            mk2 = tab[4]
            blast12[mk1] = mk2
            blast21[mk2] = mk1
    print("{:,} markers from map file {} ".format(n, in_file))
    return blast12, blast21

def read_locus2LG(in_file):
    print("read", in_file)
    locus2LG = dict()
    LGs = collections.defaultdict(int)
    n = 0
    with open(in_file) as f_in:
        for l in f_in:
            if l.endswith('\t\n'):
                continue
            n += 1
            locus, LG = l.strip().split('\t')
            # skip locus mapped on more than one LG
            if ',' in LG:
                continue
            LG = int(LG.replace('LG', ''))
            LGs[LG] += 1
            locus2LG[locus] = LG
    print("{:,} markers, {} LGs, from map file {} ".format(n, len(LGs), in_file))
    return LGs, locus2LG

if __name__ == '__main__':
    description = """ 
    compare two maps
    input : locus2LG, blast_ok, gmap

    input files formats :

    - locus2LG
    mk          LG

    - blast_ok
    #qseqid	qlen	qstart	qend	sseqid	slen	sstart	send	length	pident	evalue	score	sstrand
    test1_100017	236	1	142	mse_99192	142	1	142	142	100.000	2.37e-71	142	plus

    output example : LG1 200 mk, 100 (50%) in second map, on 3 LGs : 90 LG1, 5 LG2, 5 LG3
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--map1", help="input file for first map : locus2LG", required=True)
    parser.add_argument("--map2", help="input file for second map : locus2LG", required=True)
    parser.add_argument("--blast", help="input blast result from first map mk on second map mk", required=True)

    args = parser.parse_args()
    main() 
