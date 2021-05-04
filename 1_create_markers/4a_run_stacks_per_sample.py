#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import sfi

def main(): 
    top_dir = args.top_dir
    info_dir = "{}/info".format(args.top_dir)
    reads_dir = args.reads_dir
    res_dir = "{}/{}".format(top_dir, args.name)    
    trace_dir = "{}/trace".format(res_dir)

    samples_index = "{}/{}".format(info_dir, args.sample_index)
    list_parents = "{}/{}".format(info_dir, args.parents)
    list_progeny = "{}/{}".format(info_dir, args.progeny)

    # ustacks needs an index for each sample, always use the same index file containing all samples
    sample_index = sfi.file2dict(samples_index)
    parents = sfi.file2list(list_parents)
    progeny = sfi.file2list(list_progeny)
    samples = parents + progeny

    print("top_dir={}, reads_dir={}, res_dir={}".format(top_dir, reads_dir, res_dir))
    print("{} parents, {} progeny, {} samples".format(len(parents), len(progeny), len(samples)))

    for d in (res_dir, trace_dir):
        if not os.path.isdir(d):
            print("makedirs {}".format(d))
            os.makedirs(d)

    # from http://catchenlab.life.illinois.edu/stacks/manual/#phand
    # ustacks -f ./samples/sample_01.1.fq.gz -o ./stacks -i 1 --name sample_01 -M 4 --gapped -p 8

    # ustacks on samples
    for sample in samples:
        #print("ustacks", sample)
        index = sample_index[sample]
        # 3 outputs RESDIR/NAME_{alleles, snps, tags}.tsv.gz - RESDIR from -o, NAME from --name
        target = "{}/{}.tags.tsv.gz".format(res_dir, sample)
        trace = "{}/ustacks_{}".format(trace_dir, sample)
        # f: input file path.
        # i: a unique integer ID for this sample.
        # o: output path to write results.
        # M: Maximum distance (in nucleotides) allowed between stacks (default 2).
        # m: Minimum depth of coverage required to create a stack (default 3).
        # N: Maximum distance allowed to align secondary reads to primary stacks (default: M + 2).
        # p: enable parallel execution with num_threads threads.
        # t: input file type. Supported types: fasta, fastq, gzfasta, or gzfastq (default: guess).
        # --name: a name for the sample (default: input file name minus the suffix).
        # R: retain unused reads.
        # H: disable calling haplotypes from secondary reads.

        cmd = "ustacks -t gzfastq -f {reads_dir}/{sample}.fq.gz -o {res_dir} -i {index} --name {sample} -m {m_option} -M {M_option} -p {threads} > {trace} 2>&1".format(reads_dir=reads_dir, sample=sample, res_dir=res_dir, index=index, m_option=args.m, M_option=args.M, threads=args.p, trace=trace)
        sfi.run(args, "ustacks", target, cmd)

    # make catalog from parents
    # 3 outputs RESDIR/catalog.{alleles, snps, tags}.tsv.gs - RESDIR from -o
    target = "{}/catalog.alleles.tsv.gz".format(res_dir)
    trace = "{}/cstacks".format(trace_dir)
    files = ""
    for parent in parents: 
        files += " -s {}/{}".format(res_dir, parent)

    # remark : we can use either popmap file to specify a list of sample or -s to specify some samples
    # here use use -s to specify both parents to build catalog

    # -P,--in-path: path to the directory containing Stacks files.
    # -M,--popmap: path to a population map file. [sfi : specify samples to be used to build cataclog => unused here since we use parents]
    # -n: number of mismatches allowed between sample loci when build the catalog (default 1; suggested: set to ustacks -M).
    # -p,--threads: enable parallel execution with num_threads threads.
    # -s: sample prefix from which to load loci into the catalog.
    # -o,--outpath: output path to write results.
    # -c,--catalog <path>: add to an existing catalog.
    cmd = "cstacks {files} -o {res_dir} -n {n_option} -p {threads} > {trace} 2>&1".format(res_dir=res_dir, files=files, n_option=args.n, threads=args.p, trace=trace)
    sfi.run(args, "cstacks", target, cmd)

    # sstacks on parents and progeny
    for sample in samples:
        # remark : we can use either popmap file to specify a list of sample to be used, or -s to specify one sample
        # here we loop for each sample and run sstacks with -s to specify only one sample
        # so that it is easier to complete some sample without redoing all samples

        # -P,--in-path: path to the directory containing Stacks files.  [sfi unused, we specify the specific file for each sample]
        # -M,--popmap: path to a population map file from which to take sample names. [sfi unused, we specify the specific file for each sample]
        # -s,--sample: filename prefix from which to load sample loci. [ sfi : use this one]
        # -c,--catalog: path to the catalog. [sfi if path is a folder, then catalog will be path/catalog.*]
        # -p,--threads: enable parallel execution with n_threads threads.
        # -o,--out-path: output path to write results.
        # -x: don't verify haplotype of matching locus.

        # 1 outputs RESDIR/NAME.matches.tsv.gz - RESDIR and NAME from -s
        target = "{}/{}.matches.tsv.gz".format(res_dir, sample)
        trace = "{}/sstacks_{}".format(trace_dir, sample)
        cmd = "sstacks -c {res_dir} -s {res_dir}/{sample} -o {res_dir} -p {threads} > {trace} 2>&1".format(res_dir=res_dir, sample=sample, threads=args.p, trace=trace)
        sfi.run(args, "sstacks", target, cmd)

    # tsv2bam on parents and progeny
    for sample in samples:
        # remark : we can use either popmap file to specify a list of sample to be used, or -s to specify one sample
        # here we loop for each sample and run sstacks with -s to specify only one sample
        # so that it is easier to complete some sample without redoing all samples

        # -P,--in-dir: input directory.
        # -M,--popmap: population map. [sfi : unused]
        # -s,--sample: name of one sample. [sfi use this one]
        # -R,--pe-reads-dir: directory where to find the paired-end reads files (in fastq/fasta/bam (gz) format).
        # -t: number of threads to use (default: 1).

        # 1 output RESDIR/SAMPLE.matches.bam - RESDIR from -P, SAMPLE from -s
        target = "{}/{}.matches.bam".format(res_dir, sample)
        trace = "{}/tsv2bam_{}".format(trace_dir, sample)
        # !!!
        pe_reads_dir = "{}_pairs".format(reads_dir)
        cmd = "tsv2bam -P {res_dir} -s {sample} -R {reads_dir} -t {threads} > {trace} 2>&1".format(res_dir=res_dir, reads_dir=pe_reads_dir, sample=sample, threads=args.p, trace=trace)
        sfi.run(args, "tsv2bam", target, cmd)

if __name__ == '__main__':
    description = """ 
    Run stack comands (ustacks, cstacks, sstacks) without SQL 
    - ustacks on parents and progeny
    - cstacks on parents to create cataclog
    - sstacks on parents and progeny
    - tsv2bam on parents and progeny
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--shell", help="create a shell script to run commands", default="")
    parser.add_argument("--top_dir", help="top dir")
    parser.add_argument("--name", help="name of step")
    parser.add_argument("--parents", help="parents_file")
    parser.add_argument("--progeny", help="progeny_file")
    parser.add_argument("--sample_index", default="samples_index", help="file with index for all samples")
    parser.add_argument("--reads_dir", help="dir for fastq reads")
    parser.add_argument("-m", type=int, help="Minimum depth of coverage required to create a stack (default 3)")
    parser.add_argument("-M", type=int, help="Maximum distance (in nucleotides) allowed between stacks (default 2)")
    parser.add_argument("-n", type=int, help="number of mismatches allowed between sample tags when generating the catalog (default 0)")
    parser.add_argument("-p", type=int, help="Enable parallel execution with num_threads threads")

    args = parser.parse_args()
    if args.shell:
        print("write", args.shell)
        args.f_shell = open(args.shell, "w")
        sep = "#" * 20
        args.f_shell.write("{}\n".format(sep))
        args.f_shell.write("# {}\n".format(" ".join(sys.argv)))
        args.f_shell.write("{}\n".format(sep))
        args.f_shell.write("# {}\n".format(args))
        args.f_shell.write("{}\n".format(sep))
        #args.f_shell.write("{sep}\n# {}\n{sep}\n# {}\n#####\n".format(" ".join(sys.argv), args))

    main() 
