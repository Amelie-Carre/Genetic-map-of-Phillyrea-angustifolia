#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import yaml
import sfi

def main():
    raw = config['raw']
    parents = ['FIp003', 'FIp006']
    progeny = list()
    lib_list = list()

    script1 = "{}_dispatch.sh".format(config['name'])
    script2 = "{}_concat.sh".format(config['name'])
    top_dir = "NO_BACKUP/{}".format(config['name'])
    sample_dir = "{}/{}".format(top_dir, config['sample_dir'])
    barcodes_dir = "{}/{}".format(top_dir, config['barcodes_dir'])
    lib_dir = "{}/{}".format(top_dir, config['lib_dir'])
    log_dir = "{}/{}".format(top_dir, config['log_dir'])
    sample_file = "{}/{}".format(top_dir, config['sample_file'])
    progeny_file = "{}/{}".format(top_dir, config['progeny_file'])
    lib_file = "{}/{}".format(top_dir, config['lib_file'])

    for d in (barcodes_dir, lib_dir, log_dir, sample_dir):
        if not os.path.isdir(d):
            if args.verbose : print("make dir", d)
            os.makedirs(d)

    in_file = config['lib_desc']
    if args.verbose : print("read", in_file)
    if args.verbose : print("write", script1)
    n = 0
    with open(in_file) as f_in, open(script1, "w") as f_script1: 
        f_script1.write("#!/bin/bash\n")
        for line in f_in:
            if line.startswith('Librairie'):
                continue # skip title
            n += 1
            if n == 1:
               group = list()
            tab = line.strip().split(':')
            if tab[0]:
                the_lib = tab[0]
                the_lib = the_lib.replace('FIc', 'FIC')
                the_seqIdx = tab[2]
                lib_list.append(the_lib)
            sample = tab[3]
            if sample.startswith('Fic'):
                sample = sample.replace('Fic', 'FIc')
            if sample.startswith('FIc'):
                pass
            elif sample.startswith('FIp'):
                pass
            else:
                print('Bad sample name {}'.format(sample))
                exit(1)
            group.append((tab[5], tab[6], sample))
            if n == 8:
                n = 0

                #skip_lib = ["FIC-Pol013-1", "FIC-Pol026-1"]
                skip_lib = []
                if the_lib in skip_lib:
                    print("#skip ", the_lib)
                    continue

                barcodesFile_all = "{barcodes_dir}/lib_{lib}_all".format(barcodes_dir=barcodes_dir, lib=the_lib)
                barcodesFile_1 = "{barcodes_dir}/lib_{lib}_1".format(barcodes_dir=barcodes_dir, lib=the_lib)
                barcodesFile_2_8 = "{barcodes_dir}/lib_{lib}_2_8".format(barcodes_dir=barcodes_dir, lib=the_lib)
                file1 = "{raw}/{lib}_{seqIdx}_L002_R1.fastq.gz".format(raw=raw, lib=the_lib, seqIdx=the_seqIdx)
                file2 = "{raw}/{lib}_{seqIdx}_L002_R2.fastq.gz".format(raw=raw, lib=the_lib, seqIdx=the_seqIdx)
                #print("######### lib={}, seqIdx={}, barcodeFile={}".format(the_lib, the_seqIdx, barcodesFile))
                if not os.path.isfile(file1):
                    print("missing file {}".format(file1))
                    exit(2)
                if not os.path.isfile(file2):
                    print("missing file {}".format(file2))
                    exit(2)
                if args.verbose : print("write ", barcodesFile)
                with open(barcodesFile_all, "w") as f_all, open(barcodesFile_1, "w") as f_1, open(barcodesFile_2_8, "w") as f_2_8 :
                    for i in group:
                        (Pst, Mse, sample) = i
                        if not sample.startswith("FIp"):
                            progeny.append(sample)
                        f_all.write("{}\t{}\t{}\n".format(Pst, Mse, sample))
                        if Pst == "CGATG":
                            f_1.write("{}\t{}\t{}\n".format(Pst, Mse, sample))
                        else:
                            f_2_8.write("{}\t{}\t{}\n".format(Pst, Mse, sample))

                the_lib_dir = "{}/{}".format(lib_dir, the_lib)
                if not os.path.isdir(the_lib_dir):
                    os.makedirs(the_lib_dir)
                log = "{}/process_radtag_{}".format(log_dir, the_lib)
                if not os.path.isfile(log):
                    #cmd = "process_radtags -1 {} -2 {} -o {} -b {} --renz_1 pstI -c -q -r --inline_null > {} 2>&1".format(file1, file2, the_lib_dir, barcodesFile, log)
                    # process_radtags -1 pair_1 -2 pair_2 [-b barcode_file] -o out_dir -e enz [-c] [-q] [-r] [-t len]
                    #   b: path to a file containing barcodes for this run, omit to ignore any barcoding.
                    #   o: path to output the processed files.
                    #   1: first input file in a set of paired-end sequences.
                    #   2: second input file in a set of paired-end sequences.
                    #   c,--clean: clean data, remove any read with an uncalled base.
                    #   q,--quality: discard reads with low quality scores.
                    #   r,--rescue: rescue barcodes and RAD-Tags.
                    #   t: truncate final read length to this value.
                    #   D: capture discarded reads to a file.
                    #   Barcode options:
                    #   --inline-null:   barcode is inline with sequence, occurs only on single-end read (default).
                    #   --index-null:    barcode is provded in FASTQ header (Illumina i5 or i7 read).
                    #   --null-index:    barcode is provded in FASTQ header (Illumina i7 read if both i5 and i7 read are provided).
                    #   --inline-inline: barcode is inline with sequence, occurs on single and paired-end read.
                    #   --index-index:   barcode is provded in FASTQ header (Illumina i5 and i7 reads).
                    #   --inline-index:  barcode is inline with sequence on single-end read and occurs in FASTQ header (from either i5 or i7 read).
                    #   --index-inline:  barcode occurs in FASTQ header (Illumina i5 or i7 read) and is inline with single-end sequence (for single-end data) on paired-end read (for paired-end data).
                    #   Restriction enzyme options:
                    #   --renz-1 <enz>: provide the restriction enzyme used (cut site occurs on single-end read)
                    #   --renz-2 <enz>: if a double digest was used, provide the second restriction enzyme used (cut site occurs on the paired-end read).
                    #   Advanced options:
                    #   --filter-illumina: discard reads that have been marked by Illumina's chastity/purity filter as failing.
                    #   --disable-rad-check: disable checking if the RAD site is intact.
                    #   --len-limit <limit>: specify a minimum sequence length (useful if your data has already been trimmed).
                    #   --barcode-dist-1: the number of allowed mismatches when rescuing single-end barcodes (default 1).
                    #   --barcode-dist-2: the number of allowed mismatches when rescuing paired-end barcodes (defaults to --barcode-dist-1).

                    #options = "--renz_1 pstI --renz_2 mseI --inline_inline -c -q -r -D"
                    #options += " --filter-illumina"
                    #options += " --disable-rad-check"
                    #options += " --barcode-dist-1"
                    #options += " --barcode-dist-2"

                    options = config['process_radtag_options']
                    cmd = "process_radtags -1 {} -2 {} -o {} -b {} {} > {} 2>&1 &".format(file1, file2, the_lib_dir, barcodesFile_all, options, log)
                    if args.verbose : print(cmd)
                    f_script1.write("{}\n".format(cmd))

        f_script1.write("echo END\n")

    samples = parents + progeny

    # commands to concat reads per sample 
    if args.verbose : print("write", script2)
    with open(script2, "w") as f_script2 :
        f_script2.write("#!/bin/bash\n")

        # warning parents have 2 files (a and b)
        for sample in samples:
            cmd1 = "ls -lh {lib_dir}/*/{sample}*.gz  > {log_dir}/mk_se_{sample} &".format(sample=sample, lib_dir=lib_dir, log_dir=log_dir)
            cmd2 = "cat {lib_dir}/*/{sample}*.gz > {sample_dir}/{sample}.fq.gz &".format(sample=sample, lib_dir=lib_dir, sample_dir=sample_dir)
            if args.verbose : 
                print(cmd1)
                print(cmd2)
            f_script2.write("{}\n".format(cmd1))
            f_script2.write("{}\n".format(cmd2))
        f_script2.write("echo END\n")

    print("{} [{}] : {} libraries, {} samples (2 parents + {} progeny)".format(config['name'], config['process_radtag_options'], len(lib_list), len(samples), len(progeny)))
    sfi.list2file(progeny, progeny_file)
    sfi.list2file(samples, sample_file)
    sfi.list2file(lib_list, lib_file)

if __name__ == '__main__':
    description = """ Write a bash script which will create fastq files for each sample 
    
    1) create barcode file for stacks 
    2) extract reads using process_radtag
    3) concat forward and reverse files to a uniq file

    1) create barcode file for stacks
    input file :
    Info-Tag-GBS_Filaire_HiSeq_290615-1.csv
    # one header line
    Librairie:Index illumina:Seq index:Code AMM:Code plante:Pst:Mse:::
    # then 8 lines per library with 8 barcodes
    :::FIc001:2013-5.P-1:CGATG:TGTGACCG:::
    :::FIc002:2013-5.P-2:GCTAGA:ATCACAC:::
    :::FIc003:2013-5.P-3:ATGCCGA:CAGCTG:::
    FIC-Pol001-1:TruSeq-001:ATCACG:FIc004:2013-5.P-4:TACGCACA:GCATG:::
    :::FIc005:2013-5.P-5:CTGAT:TGCTCAGC:::
    :::FIc006:2013-5.P-6:GACTAG:ACGCTCG:::
    :::FIc008:2013-5.P-8:AGTCACG:GATAAG:::
    :::FIc009:2013-5.P-9:TCAGTCCA:CTAGG:::

    # these 8 lignes correspond to file
    # FIC-Pol001-1_ATCACG_L002_R1.fastq
    # FIC-Pol001-1_ATCACG_L002_R2.fastq
    # tahet is {lib}_{seq_index}_L002_R[12].fastq
    # always L002 (ie lane 2)
    # For each lib, creat a barcodes_LIB file
    # and prepare process_radtag command using this barcodes_LIB file

    2 first fine from barcodes_LIB file:
    CGATG	TGTGACCG	FIc001
    GCTAGA	ATCACAC		FIc002

    2) extract reads using process_radtag
    commande process_radtag :
    process_radtags -1 {raw}/{lib}_R1.fastq -2 {raw}/{lib}_R2.fastq \
    -o samples -b barcodes_{lib} --renz_1 pstI --renz_2 mseI -c -q -r --inline_inline
    """

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-f", "--force", action='store_const', const="-f", default="", help="re-create already existing output file")
    parser.add_argument("--config", help="config file")

    args = parser.parse_args()
    config = yaml.safe_load(open(args.config))
    main() 
