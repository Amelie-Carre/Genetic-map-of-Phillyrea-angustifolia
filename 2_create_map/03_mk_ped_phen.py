#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

def main():

    phens = ['sex1', 'sex2', 'sex3', 'SI1', 'SI2', 'SI3', 'SI4', 'SI5']

    print("read phneotype file for sex and SI {}".format(args.in_trait))
    sample_sex = dict()
    # sample_post[trait][sample] = string of 10 posterior_proba
    sample_post = dict()
    for phen in phens:
        sample_post[phen] = dict()
    post_hom = "1 0 0 0 0 0 0 0 0 0"
    post_het = "0 1 0 0 0 0 0 0 0 0"
    post_unk = "1 1 1 1 1 1 1 1 1 1"

    with open(args.in_trait) as f_in:
        for l in f_in:
            sample, sex = l.strip().split('\t')
            # 2 hypothesys per phen
            if sex == 'M':
                sex = '1'
                sample_post['sex1'][sample] = post_het
                sample_post['sex2'][sample] = post_hom
                sample_post['sex3'][sample] = post_hom
                sample_post['SI1'][sample] = post_unk
                sample_post['SI2'][sample] = post_unk
                sample_post['SI3'][sample] = post_unk
                sample_post['SI4'][sample] = post_unk
                sample_post['SI5'][sample] = post_unk
            elif sex == 'G1':
                sex = '2'
                sample_post['sex1'][sample] = post_hom
                sample_post['sex2'][sample] = post_het
                sample_post['sex3'][sample] = post_het
                sample_post['SI1'][sample] = post_het
                sample_post['SI2'][sample] = post_hom
                sample_post['SI3'][sample] = post_hom
                sample_post['SI4'][sample] = post_het
                sample_post['SI5'][sample] = post_hom
            elif sex == 'G2':
                sex = '2'
                sample_post['sex1'][sample] = post_hom
                sample_post['sex2'][sample] = post_het
                sample_post['sex3'][sample] = post_het
                sample_post['SI1'][sample] = post_hom
                sample_post['SI2'][sample] = post_het
                sample_post['SI3'][sample] = post_het
                sample_post['SI4'][sample] = post_hom
                sample_post['SI5'][sample] = post_het
            elif sex == '-':
                sex = '0'
                sample_post['sex1'][sample] = post_unk
                sample_post['sex2'][sample] = post_unk
                sample_post['sex3'][sample] = post_unk
                sample_post['SI1'][sample] = post_unk
                sample_post['SI2'][sample] = post_unk
                sample_post['SI3'][sample] = post_unk
                sample_post['SI4'][sample] = post_unk
                sample_post['SI5'][sample] = post_unk
            else:
                print("bad sex {} for sample {}".format(sex, sample))
                exit(0)
            sample_sex[sample] = sex
    #print(sample_sex)
    #print(sample_post)
    # add traits for parents (since they are not in trait file)
    # Father : FIp006 : S1 S2 (Hb) => G1
    sample_post['sex1'][args.father] = post_het
    sample_post['sex2'][args.father] = post_het
    sample_post['sex3'][args.father] = post_hom
    sample_post['SI1'][args.father] = post_het
    sample_post['SI2'][args.father] = post_het
    sample_post['SI3'][args.father] = post_hom
    sample_post['SI4'][args.father] = post_unk
    sample_post['SI5'][args.father] = post_unk
    # Mother : FIp003 : S1 S1 (Ha) => G2
    sample_post['sex1'][args.mother] = post_hom
    sample_post['sex2'][args.mother] = post_hom
    sample_post['sex3'][args.mother] = post_het
    sample_post['SI1'][args.mother] = post_hom
    sample_post['SI2'][args.mother] = post_hom
    sample_post['SI3'][args.mother] = post_het
    sample_post['SI4'][args.mother] = post_hom
    sample_post['SI5'][args.mother] = post_het

    print("read", args.in_progeny)
    progeny = list()
    with open(args.in_progeny) as f_in:
        for l in f_in:
            progeny.append(l.strip())

    samples = [args.mother,  args.father] + progeny

    print(len(samples), "samples")
    #print(samples)

    # file format 
    # from https://sourceforge.net/p/lep-map3/wiki/LM3%20Home/

    sep = "\t"
    print("write", args.out_ped)
    with open(args.out_ped, "w") as f_out:
        chr_pos = ["CHR", "POS"]

        # First line is the family name
        # CHR POS F   F   F   F   F   F
        tab = chr_pos + [args.familly for i in samples]
        f_out.write("{}\n".format(sep.join(tab)))

        # second individual name
        # CHR POS female  male    progeny_1   progeny_2   progeny_3   progeny_4
        tab = chr_pos + [sample for sample in samples]
        f_out.write("{}\n".format(sep.join(tab)))
    
        # third and fourth are the father and mother.
        # CHR POS 0   0   male    male    male    male
        # CHR POS 0   0   female  female  female  female
        tab = chr_pos + ["0", "0"] + [args.father for sample in progeny]
        f_out.write("{}\n".format(sep.join(tab)))
        tab = chr_pos + ["0", "0"] + [args.mother for sample in progeny]
        f_out.write("{}\n".format(sep.join(tab)))

        # Line 5 contains the sex of each individual (1 male, 2 female (<= herma), 0 unknown)
        # CHR POS 2   1   0   0   0   0
        tab = chr_pos + ["2", "1"] + [sample_sex[sample] for sample in progeny]
        f_out.write("{}\n".format(sep.join(tab)))

        # the last line is the phenotype (can be 0 for all individuals, this is not currently used).
        # CHR POS 0   0   0   0   0   0
        tab = chr_pos + ["0" for sample in samples]
        f_out.write("{}\n".format(sep.join(tab)))

    print("write", args.out_phen)
    sep = "\t"
    with open(args.out_phen, "w") as f_out:
        # write a line with hearders
        # CHR POS female  male    progeny_1   progeny_2   progeny_3   progeny_4
        tab = chr_pos + [sample for sample in samples]
        f_out.write("{}\n".format(sep.join(tab)))

        # pseudo mk lines
        # phen 1 0   0   0   0   0   0
        for phen in phens:
            #print("phen {} sample {} post {}".format(phen, sample, sample_post[phen][sample]))
            tab = [phen, '1'] + [sample_post[phen][sample] for sample in samples]
            f_out.write("{}\n".format(sep.join(tab)))


if __name__ == '__main__':
    description = """ 
    Create pedigree file and posterior proba for each trait
    coding sample posterior proba : 
    hom : AA => 1, others (AC, AG, AT, CC, CG, CT, GG, GT and TT) => 0
    het : AC => 1, others (AA, AG, AT, CC, CG, CT, GG, GT and TT) => 0
    hom = "1 0 0 0 0 0 0 0 0 0"
    het = "0 1 0 0 0 0 0 0 0 0"
    unknown = "1 1 1 1 1 1 1 1 1 1"
    phenotypes 
           Father   Mother  M    G1 (Hb S1 S2)  G2 (Ha S1 S1)
    sex1 : het      hom     het  hom            hom
    sex2 : het      hom     hom  het            het
    sex3 : hom      het     hom  het            het
    SI1  : het      hom     unk  het            hom
    SI2  : het      hom     unk  hom            het
    SI3  : hom      het     unk  hom            het
    SI4  : unk      hom     unk  het            hom
    SI5  : unk      het     unk  hom            het
    """

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("--in_parents", help="input file with samples id for mother and father", required=True)
    parser.add_argument("--in_progeny", help="input file with samples id for progeny", required=True)
    parser.add_argument("--in_trait", help="input file with samples trait for sex and SI (M/G1/G2/-)", required=True)
    parser.add_argument("--father", help="father sample id", default="FIp006")
    parser.add_argument("--mother", help="mother sample id", default="FIp003")
    parser.add_argument("--familly", help="mother sample id", default="FI")
    parser.add_argument("--out_ped", help="output file with pedigree", required=True)
    parser.add_argument("--out_phen", help="output file with phenotypes", required=True)

    args = parser.parse_args()
    main() 
