#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sfi

def main():
    l_min, l_max, l_step = args.lod.split(':')
    s_min, s_max, s_step = args.size.split(':')
    
    l_options = range(int(l_min), int(l_max) + int(l_step), int(l_step))
    s_options = range(int(s_min), int(s_max) + int(s_step), int(s_step))

    data_call = "{}/data.call".format(args.name)
    res_dir = "{}/tests".format(args.name)

    # options for lep-map3.sh SeparateChromosomes2
    # distortionLod=1    Use segregation distortion aware LOD scores [not set]
    # => distortionLod=1 since ther is only unique familly
    # lodLimit=NUM       LOD score limit [10.0]
    # ==> try some values
    # sizeLimit=NUM      Remove LGs with < NUM markers [1]
    # ==> try some values
    # numThreads=NUM     Use maximum of NUM threads [1]
    # ==> 64
    # phasedData=1       Data is phased [not set]
    # ==> phase is provided by stacks pipeline (read based phase, not statistical phase)
    # lod3Mode=NUM       Controls how LOD scores are computed between double informative markers [1]
    #                     1: haplotypes match (4 alleles, max LOD = log(4^n)
    #                     2: homozygotes match (3 alleles, max LOD = log(3^n))
    #                     3: homozygotes or heterozygotes match (2 alleles, max LOD = log(2^n))
    # informativeMask=STR     Use only markers with informative father (1), mother(2), both parents(3) or neither parent(0) [0123]
    # ==> try default [0123] for all lod
    # map=file           refine linkage group lg of map file
    # lg=NUM             refine linkage group lg [1 if map is provided]
    # renameLGs=0        do not rename linkage groups after refine

    for l in l_options:
        for s in s_options:
            name = "map_l_{l}_s_{s}".format(l=l, s=s)

            # run SeparateChromosome2
            map_file = "{res_dir}/{name}.txt".format(res_dir=res_dir, name=name)
            trace_file = "{res_dir}/trace/6a_sp_{name}.txt".format(res_dir=res_dir, name=name)
            options = "data={data} lodLimit={l} sizeLimit={s} distortionLod=1 phasedData=1 numThreads=64".format(data=data_call, l=l, s=s)
            target = map_file
            cmd = "lep-map3.sh SeparateChromosomes2 {options} > {map_file} 2> {trace_file}".format(options=options, map_file=map_file, trace_file=trace_file)
            sfi.run(args, "SeparateChrom", target, cmd)

            # refine map
            suffix="rsrcsrc"
            new_name   = "{name}{suffix}".format(name=name, suffix=suffix)
            trace_file = "{res_dir}/trace/6b_metrics_{name}.txt".format(res_dir=res_dir, name=new_name)
            target = "{res_dir}/{name}.txt".format(res_dir=res_dir, name=new_name)
            cmd = "sh ./6c_LG_polish_v2.sh {name} {lod} {size} map {data_call}".format(name=args.name, lod=l, size=s, data_call=data_call)
            sfi.run(args, "LG_refine", target, cmd)

            # run metrics on various map steps
            for suffix in ['', 'rsr', 'rsrc', 'rsrcsr', 'rsrcsrc' ]:
                new_name   = "{name}{suffix}".format(name=name, suffix=suffix)
                new_map_file = "{res_dir}/{name}.txt".format(res_dir=res_dir, name=new_name)
                xls_file   = "{res_dir}/metrics/{name}/{name}_metrics.xls".format(res_dir=res_dir, name=new_name)
                out_dir    = "{res_dir}/metrics/{name}".format(res_dir=res_dir, name=new_name)
                trace_file = "{res_dir}/trace/6b_metrics_{name}.txt".format(res_dir=res_dir, name=new_name)
                target = xls_file
                cmd = "./6b_LG_metrics_v2.py --in_data {data} --in_map {map_file} --out_dir {out_dir} > {trace_file} 2>&1".format(data=data_call, map_file=new_map_file, trace_file=trace_file, out_dir=out_dir)
                sfi.run(args, "LG_metrics", target, cmd)

if __name__ == '__main__':
    description = """ run separate chrom with various options, refine map and compute statistics on maps """

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("-v", "--verbose", action="store_const", const="-v", default="")
    parser.add_argument("-t", "--test", action="store_const", const="-t", default="")
    parser.add_argument("--shell", help="create a shell script to run commands", default="")
    parser.add_argument("--name", help="sn2, sn3", required=True)
    parser.add_argument("--lod", help="lodscore min:max:step", required=True)
    parser.add_argument("--size", help="LG size min:max:step", required=True)

    args = parser.parse_args()
    main() 

