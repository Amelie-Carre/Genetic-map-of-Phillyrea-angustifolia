#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse

def main(): 

    # LG 23 has no markers and should be ignored
    chroms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24]
    sexs = [0, 1]
    reps = [1, 2, 3]

    for chrom in chroms:
        for sex in sexs:
            best_val = 0
            best_rep = 0
            all_val = list()
            for rep in reps:
                name = "final_{}_LG_{}_{}_{}".format(args.map, chrom, sex, rep)
                trace_file = "sn2/trace/7a_om_map_{}".format(name)
                val = get_val(trace_file)
                all_val.append(val)
                if val > best_val:
                    best_val = val
                    best_rep = rep
                #print("chrom {} sex {} rep {} : val {} best val {} best rep {}".format(chrom, sex, rep, val, best_val, best_rep))

            #print("chrom {} sex {} : best val {}, best rep {}, all val {}".format(chrom, sex, best_val, best_rep, all_val))
            new_map = "sn2/final_best_{}_LG_{}_{}.txt".format(args.map, chrom, sex)
            best_map = "final_{}_LG_{}_{}_{}.txt".format(args.map, chrom, sex, best_rep)
            cmd = "ln -s {} {}".format(best_map, new_map)
            os.system(cmd)
            min_val = min(all_val)
            max_val = max(all_val)
            diff_val = max_val - min_val
            print("chrom {} sex {} : best rep {}, min val {}, max val {}, diff val {}".format(chrom, sex, best_rep, min_val, max_val, diff_val))
            
def get_val(in_file):
    #print("read", in_file)
    if not os.path.isfile(in_file):
        print("missing", in_file)
        exit(1)
    with open(in_file) as f_in:
        for l in f_in:
            if l.startswith('logL ='):
                tmp = l.replace('logL = ', '')
                return abs(float(tmp))
    print("Error {} : no line logL =".format(in_file))
    exit(1)
    	    
if __name__ == '__main__':
    description = """ collect best map from 3 replicates """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--map", help="map file", required=True)
    args = parser.parse_args()

    main() 


