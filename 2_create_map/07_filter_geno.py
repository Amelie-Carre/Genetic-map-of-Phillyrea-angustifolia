#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

def main():
    print("in {} => out {}, min cov per ind to call a genotype".format(args.in_file, args.out_file, args.min_cov))
    n_col = 0
    n_ind = 0
    n_mk = 0
    all_loci = set()
    all_snps = set()
    modif_loci = set()
    modif_snps = set()
    n_modif_geno = 0
    n_all_geno = 0
    n_line = 0
    with open(args.in_file) as f_in, open(args.out_file, 'w') as f_out:
        for l in f_in:
            n_line += 1
            tab = l.strip().split('\t')
            if n_ind == 0:
                n_col = len(tab)
                # col number for ind = number of cols minus first 2 cols, divided by 4 (4 cols per ind)
                n_ind = int((n_col - 2) / 4)
                print("{} cols => n_ind={}".format(n_col, n_ind))
            else:
                # skip lines with invalid column number
                if len(tab) != n_col:
                    print("skip line {} : {} cols instead of {}".format(n_line, len(tab), n_col))
                    continue
            all_loci.add(tab[0])
            all_snps.add("{}_{}".format(tab[0], tab[1]))
            new_tab = tab[0:3]
            for i in range(n_ind):
                start = 3 + i * 4
                end = start + 4
                tab2 = tab[start:end]
                # check there are 4 cols per ind
                if len(tab2) != 4:
                    print("Pb line {} ind {} start {} end {} => {}".format(n_line, i, start, end, tab2))
                    print(l)
                    print(tab)
                    exit(1)
                depth, seq, q1, q2 = tab2
                # check cover >= args.min_cov
                if int(int(depth) >= args.min_cov):
                    # if OK, keep genotype
                    new_tab.extend(tab2)
                    n_all_geno += 1
                    #print("ind {} : {} {}".format(i, depth, seq))
                else:
                    # set genotype as "unknown"
                    new_tab.extend(['0', '', '*',	'*'])
                    n_modif_geno += 1
                    modif_loci.add(tab[0])
                    modif_snps.add("{}_{}".format(tab[0], tab[1]))
                    #print("ind {} : {} {} ===> 0".format(i, depth, seq))
            # write line with all ind
            f_out.write("{}\n".format("\t".join(new_tab)))

    # report count
    n_modif_snps = len(list(modif_snps))
    n_modif_loci = len(list(modif_loci))
    n_all_snps = len(list(all_snps))
    n_all_loci = len(list(all_loci))
    pct_modif_geno = n_modif_geno / n_all_geno * 100
    pct_modif_snps = n_modif_snps / n_all_snps * 100
    pct_modif_loci = n_modif_loci / n_all_loci * 100
    summary_geno = "{:.2f}% [{:,}/{:,}]".format(pct_modif_geno, n_modif_geno, n_all_geno)
    summary_snps = "{:.2f}% [{:,}/{:,}]".format(pct_modif_snps, n_modif_snps, n_all_snps)
    summary_loci = "{:.2f}% [{:,}/{:,}]".format(pct_modif_loci, n_modif_loci, n_all_loci)
    print("{} modif geno, {} modif snp, {} modif loci".format(summary_geno, summary_snps, summary_loci))
    print("modif_snps : {}".format(modif_snps))
    print("modif_loci : {}".format(modif_loci))

if __name__ == '__main__':
    description = """
    filter tmp file to set "unknown genotype" when depth per ind < threshold
    file format : seq_name  pos nuc IND1 IND2 ...
    IND = 4 cols : depth seq q1 q2
    if depth < threhold (args.min_cov)
    then replace these cols by these 4 cols : 0		*	*	

    one line exemple with \n added to separate groups of 4 cols
sn2_1321_143bp	40	N	
26	CTTCCTCCCCCCTCCCTCTCTCCTTC	KKKKKKKKKKKKKKKKFKFKKKKKKK	KKIIIKIIIIIIII889898988998	
17	TTTTTTTTTTTTTTTTT	KKKKKKKKKKKKKFFKK	K8KKKKKKKKKK88889	
4	TTTT	KKK<	8888	
0		*	*	

    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--min_cov", type=int, help="min cover per ind to call a genotype", default=5)
    parser.add_argument("in_file", help="input file", required=True)
    parser.add_argument("out_file", help="output file", required=True)
    
    args = parser.parse_args()
    main() 
