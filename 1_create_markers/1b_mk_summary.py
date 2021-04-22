#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import yaml
import xlwt
import sfi

def main():

    top_dir = "NO_BACKUP/{}".format(config['name'])
    lib_file = "{}/{}".format(top_dir, config['lib_file'])
    libs = sfi.file2list(lib_file)

    data = dict()
    data['sample2tag'] = dict()
    data['sample2lib'] = dict()
    data['per_sample'] = dict()
    data['per_lib'] = dict()

    #for the_lib in libs[0:2]: 
    for the_lib in libs:
        read_trace_file(data, the_lib)
    export_data(data)

def export_data(data):
    top_dir = "NO_BACKUP/{}".format(config['name'])
    summary_yaml = "{}/{}_{}.yaml".format(top_dir, config['summary'], config['name'])
    summary_csv = "{}/{}_{}.csv".format(top_dir, config['summary'], config['name'])
    summary_xls = "{}/{}_{}.xls".format(top_dir, config['summary'], config['name'])

    if args.verbose: print("write", summary_yaml)
    with open(summary_yaml, 'w') as outfile:
        yaml.dump(data, outfile)

    if args.verbose: print("write", summary_xls)
    wb = xlwt.Workbook()
    ws1 = wb.add_sheet("per_lib")
    ws2 = wb.add_sheet("per_sample")
    # xls format for line and col titles
    fmt_title = xlwt.easyxf('font: name Times New Roman, color-index black, bold on')
    # xls format for selected lines
    fmt_selected = xlwt.easyxf('font: name Times New Roman, color-index blue, bold on')

    # per lib sheet
    l = 0; c = 0
    ws1.write(l, c, "Lib", fmt_title); c += 1
    for cell in data['libs_title']:
        ws1.write(l, c, cell, fmt_title); c += 1
    
    for the_lib in sorted(list(data['per_lib'])):
        l += 1; c = 0
        ws1.write(l, c, the_lib, fmt_title); c += 1
        for val in data['per_lib'][the_lib]:
            ws1.write(l, c, val); c += 1

    # per sample sheet
    l = 0; c = 0
    ws2.write(l, c, "Sample", fmt_title); c += 1
    ws2.write(l, c, "Barcode_N", fmt_title); c += 1
    for cell in data['samples_title']:
        ws2.write(l, c, cell, fmt_title); c += 1
    
    for sample in sorted(list(data['per_sample'])):
        l += 1; c = 0
        ws2.write(l, c, sample, fmt_title); c += 1
        ws2.write(l, c, data['sample2tag'][sample]); c += 1
        for val in data['per_sample'][sample]:
            ws2.write(l, c, val); c += 1
    wb.save(summary_xls)

def read_trace_file(data, the_lib):
    top_dir = "NO_BACKUP/{}".format(config['name'])
    trace_file = "{}/{}/{}/process_radtags.RawData.log".format(top_dir, config['lib_dir'], the_lib)
    if not os.path.isfile(trace_file):
        print("missing file {}".format(trace_file))
        exit(2)

    if args.verbose : print("read", trace_file)
    state = 0
    with open(trace_file) as f_in:
        for line in f_in:
            line = line.strip()
            # manages state's change
            if state == 0 and line.startswith('File	Retained Reads	Low Quality	Barcode Not Found	RAD cutsite Not Found	Total'):
                data['libs_title'] = line.split('\t')
                state = 1
            elif state == 1 and line.startswith('Barcode	Filename	Total	NoRadTag	LowQuality	Retained'):
                data['samples_title'] = line.split('\t')
                state = 2
                tag = 0
            elif state == 2 and line.startswith('Barcode	Total'):
                state = 3
            # work for state 1
            elif state == 1 and line.startswith('FIC'):
                tmp = line.split('\t')
                for i in (1, 2, 3, 4, 5):
                    tmp[i] = int(tmp[i])
                data['per_lib'][the_lib] = tmp

                #print("state 1 : add per_lib data for lib {} : {}".format(the_lib, data['per_lib'][the_lib]))
            # work for state 2
            elif state == 2:
                tab = line.split('\t')
                if len(tab) == 6:
                    tag += 1
                    sample = tab[1]
                    data['sample2tag'][sample] = tag
                    data['sample2lib'][sample] = the_lib
                    for i in (2, 3, 4, 5):
                        tab[i] = int(tab[i])
                    data['per_sample'][sample] = tab
                    #print("state 2 : add per_sample data for sample {} : {}".format(the_lib, data['per_sample'][sample]))

if __name__ == '__main__': 
    description = """ Collect counts per lib and per sample """

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-f", "--force", action='store_const', const="-f", default="", help="re-create already existing output file")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--config", help="config file")

    args = parser.parse_args()
    config = yaml.safe_load(open(args.config))
    main() 


