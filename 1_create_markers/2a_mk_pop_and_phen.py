#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import collections

def main(args):
    count = collections.Counter()
    # output file name
    # phen trait = M/F G1/G2
    file_phen_trait_sex = "{}/phen_trait_sex".format(args.out_dir)
    file_phen_trait_SI = "{}/phen_trait_SI".format(args.out_dir)
    file_phen_trait_sex_SI = "{}/phen_trait_sex_SI".format(args.out_dir)
    file_phen_mk_sex = "{}/phen_mk_sex".format(args.out_dir)
    file_phen_mk_SI = "{}/phen_mk_SI".format(args.out_dir)

    # for stacks
    samples_index = "{}/samples_index".format(args.out_dir)
    # all samples in an unique pop names samples
    popmap_samples = "{}/popmap_samples.tsv".format(args.out_dir)
    # all progeny in an unique pop names progeny
    popmap_progeny = "{}/popmap_progeny.tsv".format(args.out_dir)
    # parent in one pop named parents and progeny in a second pop names progeny
    popmap_parents_progeny = "{}/popmap_parents_progeny.tsv".format(args.out_dir)
    # parents and progeny in various pop names after phenotype (M, G1, G2)
    popmap_phen = "{}/popmap_phen.tsv".format(args.out_dir)

    # for lepmap3
    list_parents = "{}/list_parents".format(args.out_dir)
    list_progeny = "{}/list_progeny".format(args.out_dir)
    list_samples = "{}/list_samples".format(args.out_dir)

    parents = list()
    progeny = list()
    sample2pheno = dict()

    with open(args.in_phen) as f_in, open(file_phen_trait_sex, 'w') as f_trait_sex, open(file_phen_trait_SI, 'w') as f_trait_SI, open(file_phen_trait_sex_SI, 'w') as f_trait_sex_SI, open(file_phen_mk_sex, 'w') as f_mk_sex, open(file_phen_mk_SI, 'w') as f_mk_SI:
        n = 0
        for l in f_in:
            if l.startswith('#'):
                continue
            tab = l.strip().split(',')
            sample = tab[1]
            pheno = tab[3]
            sample2pheno[sample] = pheno
            if sample.startswith('FIp'):
                parents.append(sample)
                continue
            progeny.append(sample)
            if pheno == 'M':
                phen_trait_sex = 'M'
                phen_trait_SI = '-'
                phen_trait_sex_SI = 'M'
                phen_mk_sex = 'np'
                phen_mk_SI = '-'
                sex = 'np'
                SI = '--'
                count['M'] += 1
                count['OK'] += 1
            elif pheno == 'G1':
                phen_trait_sex = 'F'
                phen_trait_SI = 'G1'
                phen_trait_sex_SI = 'G1'
                phen_mk_sex = 'nn'
                phen_mk_SI = 'np'
                sex = 'nn'
                SI = 'np'
                count['G1'] += 1
                count['OK'] += 1
            elif pheno == 'G2':
                phen_trait_sex = 'F'
                phen_trait_SI = 'G2'
                phen_trait_sex_SI = 'G1'
                phen_mk_sex = 'nn'
                phen_mk_SI = 'nn'
                sex = 'nn'
                SI = 'nn'
                count['G2'] += 1
                count['OK'] += 1
            else:
                phen_trait_sex = '-'
                phen_trait_SI = '-'
                phen_trait_sex_SI = '-'
                phen_mk_sex = '-'
                phen_mk_SI = '-'
                sex = '--'
                SI = '--'
                count['missing'] += 1

            n += 1
            f_trait_sex.write("{}\t{}\n".format(sample, phen_trait_sex))
            f_trait_SI.write("{}\t{}\n".format(sample, phen_trait_SI))
            f_trait_sex_SI.write("{}\t{}\n".format(sample, phen_trait_sex_SI))
            f_mk_sex.write("{}\t{}\n".format(sample, phen_mk_sex))
            f_mk_SI.write("{}\t{}\n".format(sample, phen_mk_SI))

    print("{} samples written to {}".format(n, file_phen_trait_sex))
    print("{} samples written to {}".format(n, file_phen_trait_SI))
    print("{} samples written to {}".format(n, file_phen_trait_sex_SI))
    print("{} samples written to {}".format(n, file_phen_mk_sex))
    print("{} samples written to {}".format(n, file_phen_mk_SI))

    # write sample index
    with open(samples_index, 'w') as f_out:
        n = 0
        f_out.write("FIp003\t9003\n"); n += 1
        f_out.write("FIp006\t9006\n"); n += 1
        for sample in sorted(progeny):
            index = int(sample.replace('FIc', ''))
            f_out.write("{}\t{}\n".format(sample, index)); n += 1;
    print("{} samples written to {}".format(n, samples_index))
        
    # all samples in an unique pop named samples
    with open(popmap_samples, 'w') as f_out:
        n = 0
        pop = "samples"
        f_out.write("FIp003\t{}\n".format(pop)); n += 1
        f_out.write("FIp006\t{}\n".format(pop)); n += 1
        for sample in progeny:
            f_out.write("{}\t{}\n".format(sample, pop)); n += 1
    print("{} samples written to {}".format(n, popmap_samples))

    # all progeny in an unique pop named progeny
    with open(popmap_progeny, 'w') as f_out:
        n = 0
        for sample in progeny:
            f_out.write("{}\tprogeny\n".format(sample)); n += 1
    print("{} samples written to {}".format(n, popmap_progeny))

    # parent in one pop named parents and progeny in a second pop named progeny
    with open(popmap_parents_progeny, 'w') as f_out:
        n = 0
        f_out.write("FIp003\tparents\n"); n += 1
        f_out.write("FIp006\tparents\n"); n += 1
        for sample in progeny:
            f_out.write("{}\tprogeny\n".format(sample)); n += 1
    print("{} samples written to {}".format(n, popmap_parents_progeny))

    # parents and progeny in various pop names after phenotype (M, G1, G2)
    with open(popmap_phen, 'w') as f_out:
        n = 0
        f_out.write("FIp003\t{}\n".format(sample2pheno[sample])); n += 1
        f_out.write("FIp006\t{}\n".format(sample2pheno[sample])); n += 1
        for sample in progeny:
            f_out.write("{}\t{}\n".format(sample, sample2pheno[sample])); n += 1
    print("{} samples written to {}".format(n, popmap_phen))

    # list_parents
    with open(list_parents, 'w') as f_out:
        n = 0
        f_out.write("FIp003\n"); n += 1
        f_out.write("FIp006\n"); n += 1
    print("{} samples written to {}".format(n, list_parents))

    # list_progeny
    with open(list_progeny, 'w') as f_out:
        n = 0
        for sample in progeny:
            f_out.write("{}\n".format(sample)); n += 1
    print("{} samples written to {}".format(n, list_progeny))

    # list_samples
    with open(list_samples, 'w') as f_out:
        n = 0
        f_out.write("FIp003\n"); n += 1
        f_out.write("FIp006\n"); n += 1
        for sample in progeny:
            f_out.write("{}\n".format(sample)); n += 1
    print("{} samples written to {}".format(n, list_samples))

    print(count)

if __name__ == '__main__':
    description = """ Create some files with samples names and traits files from phenotype file 
    # used by stacks
    OUPUT_DIR/samples_index : use by stacks
    OUPUT_DIR/popmap_pop.tsv : use by lepmap3 : all samples in one pop (pop1)
    OUPUT_DIR/popmap_phen.tsv : use by lepmap3 : sample pop = phenotype (M, G1, G2)
    OUPUT_DIR/phen_trait_sex
    OUPUT_DIR/phen_trait_SI
    OUPUT_DIR/phen_trait_sex_SI
    OUPUT_DIR/phen_mk_sex
    OUPUT_DIR/phen_mk_SI
    # used by lepmap3
    OUPUT_DIR/list_parents
    OUPUT_DIR/list_progeny
    OUPUT_DIR/list_samples
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--in_phen", help="input phenotypes from PSL")
    parser.add_argument("--out_dir", help="output_dir for new files")

    args = parser.parse_args()
    main(args) 
