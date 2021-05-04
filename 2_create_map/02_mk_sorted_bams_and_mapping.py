#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

def main():

    parents_file = args.in_parents
    progeny_file = args.in_progeny
    mapping_file = args.out_mapping
    bams_file = args.out_bams

    samples = list()
    print("read", parents_file)
    with open(parents_file) as f_in:
        for l in f_in:
            samples.append(l.strip())

    print("read", progeny_file)
    with open(progeny_file) as f_in:
        for l in f_in:
            samples.append(l.strip())

    print(len(samples), "samples")
    print(samples)

    print("write", mapping_file)
    with open(mapping_file, "w") as f_out:
        line = " ".join(samples)
        f_out.write("{}\n".format(line))

    print("write", bams_file)
    with open(bams_file, "w") as f_out:
        line = " ".join(["{}/{}.bam".format(args.bams_dir, sample) for sample in samples])
        f_out.write("{}\n".format(line))

if __name__ == '__main__':
    description = """
    create sorted_bams file mapping.txt file from list_parents + list_progeny 
    input parents file format : 1 line per sample id
    ex : 
    FIp003
    FIp006
    input progeny file format : 1 line per sample id
    ex : 
    FIc021
    FIc070
    output sorted_bams file, format : 1 unique line with path to bam for each sample (same order as mapping : mother, father, progeny)
    ex : data/FIp003.matches.bam data/FIp006.matches.bam data/FIc021.matches.bam data/FIc070.matches.bam
    output mapping.txt file, format : 1 unique line with samples id (same order as sorted bams : mother, father, progeny)
    FIp003 FIp006 FIc021 FIc070
    """

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("--in_parents", help="input file with samples id for mother and father", required=True)
    parser.add_argument("--in_progeny", help="input file with samples id for progeny", required=True)
    parser.add_argument("--bams_dir", help="dir with bam files", required=True)
    parser.add_argument("--out_mapping", help="output file with mapping info", required=True)
    parser.add_argument("--out_bams", help="output file with list of bam files", required=True)

    args = parser.parse_args()
    main() 


