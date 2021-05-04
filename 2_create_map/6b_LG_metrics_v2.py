#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import collections
import argparse
import xlwt

def main(): 
    count = collections.Counter()

    if not os.path.isdir(args.out_dir):
        print("makedirs {}".format(args.out_dir))
        os.makedirs(args.out_dir)

    name = args.out_dir.split('/')[-1]
    print("args.out_dir {} name {}".format(args.out_dir, name))
    file_metrics = "{}/{}_metrics.xls".format(args.out_dir, name)
    file_snp2LG = "{}/{}_snp2LG.txt".format(args.out_dir, name)
    file_locus2LG = "{}/{}_locus2LG.txt".format(args.out_dir, name)
    file_mapped_loci = "{}/{}_mapped_loci.txt".format(args.out_dir, name)
    file_unmapped_loci = "{}/{}_unmapped_loci.txt".format(args.out_dir, name)
    #print(file_metrics, file_snp2LG, file_locus2LG, file_mapped_loci, file_unmapped_loci )

    # read map
    line2ID = read_data(args.in_data, count)

    # read data
    snp2LG, locus2LG = read_map(line2ID, args.in_map, count)

    # check
    bad_loci = check_LG(snp2LG, locus2LG, count)
    
    # count OK snps and loci (ie removing bad loci)
    OK_count = collections.defaultdict(int)
    OK_loci  = collections.defaultdict(set)
    for snp in snp2LG:
        seq, pos = snp
        LG = snp2LG[snp]
        #print "seq {} pos {} LG {}".format(seq, pos, LG)
        if seq not in bad_loci:
            OK_count["LG_{}".format(LG)] += 1
            OK_loci[LG].add(seq)
    for LG in OK_loci:
        OK_count["loci_in_LG_{}".format(LG)] = len(OK_loci[LG])
    #print(OK_count)

    # output 
    write_metrics(file_metrics, snp2LG, locus2LG, bad_loci, count, OK_count)
    write_snp2LG(snp2LG, file_snp2LG)
    write_locus2LG(locus2LG, file_locus2LG)
    write_mapped_loci(file_mapped_loci, file_unmapped_loci, locus2LG, bad_loci)

def write_metrics(out_file, snp2LG, locus2LG, bad_loci, count, OK_count):
    print("write", out_file)
    wb = xlwt.Workbook()
    ws1 = wb.add_sheet("summary")
    ws2 = wb.add_sheet("LG")
    ws3 = wb.add_sheet("bad_loci")
    # xls format for line and col titles
    fmt_title = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')
    # xls format for selected lines
    fmt_selected = xlwt.easyxf('font: name Times New Roman, color-index blue, bold on')

    # summary
    ws = ws1
    # head
    l = 0

    ws.write(l, 0, 'input map', fmt_title)
    ws.write(l, 1, args.in_map)
    l += 1
    ws.write(l, 0, 'input data', fmt_title)
    ws.write(l, 1, args.in_data)
    l += 1

    ws.write(l, 0, 'LGs', fmt_title)
    ws.write(l, 1, count['LGs'])
    l += 1
    ws.write(l, 0, 'loci', fmt_title)
    ws.write(l, 1, count['loci'])
    l += 1
    ws.write(l, 0, 'loci mapped', fmt_title)
    ws.write(l, 1, count['loci_mapped'])
    ws.write(l, 2, "{:.2f} %".format(float(count['loci_mapped']) / count['loci'] * 100))
    l += 1
    ws.write(l, 0, 'loci unmapped', fmt_title)
    ws.write(l, 1, count['loci_unmapped'])
    ws.write(l, 2, "{:.2f} %".format(float(count['loci_unmapped']) / count['loci'] * 100))
    l += 1
    ws.write(l, 0, 'loci bad mapped (> 1 LG)', fmt_title)
    ws.write(l, 1, count['bad_loci'])
    ws.write(l, 2, "{:.2f} %".format(float(count['bad_loci']) / count['loci'] * 100))
    l += 1
    ws.write(l, 0, 'snps in data', fmt_title)
    ws.write(l, 1, count['snps_in_data'])
    l += 1
    ws.write(l, 0, 'snps in map', fmt_title)
    ws.write(l, 1, count['snps_in_map'])
    l += 1
    ws.write(l, 0, 'snps mapped', fmt_title)
    ws.write(l, 1, count['snps_mapped'])
    ws.write(l, 2, "{:.2f} %".format(float(count['snps_mapped']) / count['snps_in_map'] * 100))
    l += 1
    ws.write(l, 0, 'snps unmapped', fmt_title)
    ws.write(l, 1, count['snps_unmapped'])
    ws.write(l, 2, "{:.2f} %".format(float(count['snps_unmapped']) / count['snps_in_map'] * 100))
    
    # LG
    ws = ws2
    # head
    l = 0; c = 0
    for cell in ['LG', 'snp_nb', 'loci_nb', 'OK_snp_nb', 'OK_loci_nb']:
        ws.write(l, c, cell, fmt_title); c += 1
    l += 1; c = 0
    # lines
    for i in range(count['LGs']):
        LG = "LG_{}".format(i)
        ws.write(l, 0, LG)
        ws.write(l, 1, count[LG])
        ws.write(l, 2, count['loci_in_LG_{}'.format(i)])
        ws.write(l, 3, OK_count[LG])
        ws.write(l, 4, OK_count['loci_in_LG_{}'.format(i)])
        l += 1

    # bad_snp sheet
    ws = ws3
    # head
    l = 0; c = 0
    for cell in ['locus', 'pos', 'LGs']:
        ws.write(l, c, cell, fmt_title); c += 1
    l += 1; c = 0
    # lines
    if len(bad_loci) > 0:
        for ID in sorted(snp2LG):
            locus, pos = ID
            if locus not in bad_loci:
                continue
            LG = snp2LG[ID]
            for val in (locus, pos, LG):
                ws.write(l, c, val); c += 1
            l += 1; c = 0

    wb.save(out_file)

def check_LG(snp2LG, locus2LG, count):
    n = 0
    bad_loci = set()

    for locus in sorted(locus2LG):
        LGs = locus2LG[locus]
        if '0' in LGs : 
            LGs.remove('0')
        if len(LGs) == 0:
            count['loci_unmapped'] += 1
        elif len(LGs) == 1:
            count['loci_mapped'] += 1
        else:
            # print("!! {} {} LGs : {}".format(locus, len(LGs), LGs))
            n += 1
            bad_loci.add(locus)

    count['bad_loci'] = len(bad_loci)

    print("QC : {} loci mapped on more than one LG".format(n))
    return bad_loci

def write_mapped_loci(mapped_loci_file, unmapped_loci_file, locus2LG, bad_loci):
    n_mapped = 0
    n_unmapped = 0
    with open(mapped_loci_file, 'w') as f_mapped, open(unmapped_loci_file, 'w') as f_unmapped:
        for locus in sorted(locus2LG):
            LGs = locus2LG[locus]
            if '0' in LGs : 
                LGs.remove('0')
            # event bad mapped loci
            if len(LGs) > 0:
                f_mapped.write("{}\n".format(locus))
                n_mapped += 1
            else:
                f_unmapped.write("{}\n".format(locus))
                n_unmapped += 1
    print("{} mapped loci written to {}, {} unmapped loci written to {}".format(n_mapped, mapped_loci_file, n_unmapped, unmapped_loci_file))

def write_locus2LG(locus2LG, out_file):
    n = 0
    with open(out_file, 'w') as f_out:
        for locus in sorted(locus2LG):
            f_out.write("{}\t{}\n".format(locus, ", ".join(sorted(list(locus2LG[locus])))))
            n += 1
    print("{} loci written to {}".format(n, out_file))

def write_snp2LG(snp2LG, out_file):
    n = 0
    with open(out_file, 'w') as f_out:
        for ID in sorted(snp2LG):
            f_out.write("{}\t{}\n".format("_".join(ID), snp2LG[ID]))
            n += 1
    print("{} mapped snp written to {}".format(n, out_file))

def read_map(line2ID, in_file, count):
    snp2LG = dict()
    locus2LG = collections.defaultdict(set)
    LG2locus = collections.defaultdict(set)
    LGs = set()
    n = 0
    with open(in_file) as f_in:
        for l in f_in:
            if l.startswith('#'):
                continue
            count['snps_in_map'] += 1
            n += 1
            LG = int(l.strip())
            LGs.add(LG)
            if LG == 0:
                count['snps_unmapped'] += 1
            else:
                count['snps_mapped'] += 1
            count['LG_{}'.format(LG)] += 1
            ID = line2ID[n]
            locus, pos = ID
            snp2LG[ID] = LG
            locus2LG[locus].add(str(LG))
            LG2locus[LG].add(str(locus))
    # if some LG have no locus, they are not present in set LGs, add them
    for LG in range(max(LGs) + 1):
        if LG not in LGs:
            LGs.add(LG)

    print("{} markers read from map file {}".format(n, in_file))
    count['LGs'] = len(LGs)
    count['loci'] = len(locus2LG)
    for LG in LG2locus:
        count['loci_in_LG_{}'.format(LG)] = len(LG2locus[LG])
    return snp2LG, locus2LG

def read_data(in_file, count):
    # line number of mk => mk_name + mk_pos
    line2ID = dict()
    n = 0
    with open(in_file) as f_in:
        for l in f_in:
            if l.startswith('#'):
                continue
            if l.startswith('CHR'):
                continue
            n += 1
            tab = l.strip().split('\t')[0:2]
            line2ID[n] = (tab[0], tab[1])
    count['snps_in_data'] = n
    print("{} mk from {}".format(n, in_file))
    return line2ID

if __name__ == '__main__':
    description = """ 
    compute metrics on map from SeparateChromosome
    input : map + data_call
    ouput : metrics.xls, mapped_loci.txt, snp2LG, locus2LG
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--in_map", help="map from SeparateChromosome", required=True)
    parser.add_argument("--in_data", help="input data in lepmap3 format", required=True)
    parser.add_argument("--out_dir", help="dir for output files", required=True)

    args = parser.parse_args()
    main() 
