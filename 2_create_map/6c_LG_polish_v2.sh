n=$1
lod=$2
size=$3
name=$4
data_call=$5

ID=${name}_l_${lod}_s_${size}

suffix0=''
suffix1=r
suffix2=rs
suffix3=rsr
suffix4=rsrc
suffix5=rsrcs
suffix6=rsrcsr
suffix7=rsrcsrc

map0=$n/tests/${ID}${suffix0}.txt
map1=$n/tests/${ID}${suffix1}.txt
map2=$n/tests/${ID}${suffix2}.txt
map3=$n/tests/${ID}${suffix3}.txt
map4=$n/tests/${ID}${suffix4}.txt
map5=$n/tests/${ID}${suffix5}.txt
map6=$n/tests/${ID}${suffix6}.txt
map7=$n/tests/${ID}${suffix7}.txt

trace1=$n/tests/trace/6c_polish_${ID}${suffix1}
trace2=$n/tests/trace/6c_polish_${ID}${suffix2}
trace3=$n/tests/trace/6c_polish_${ID}${suffix3}
trace4=$n/tests/trace/6c_polish_${ID}${suffix4}
trace5=$n/tests/trace/6c_polish_${ID}${suffix5}
trace6=$n/tests/trace/6c_polish_${ID}${suffix6}
trace7=$n/tests/trace/6c_polish_${ID}${suffix7}

loci2LG0=$n/tests/metrics/${ID}${suffix0}/${ID}${suffix0}_locus2LG.txt
loci2LG1=$n/tests/metrics/${ID}${suffix1}/${ID}${suffix1}_locus2LG.txt
loci2LG2=$n/tests/metrics/${ID}${suffix2}/${ID}${suffix2}_locus2LG.txt
loci2LG3=$n/tests/metrics/${ID}${suffix3}/${ID}${suffix3}_locus2LG.txt
loci2LG4=$n/tests/metrics/${ID}${suffix4}/${ID}${suffix4}_locus2LG.txt
loci2LG5=$n/tests/metrics/${ID}${suffix5}/${ID}${suffix5}_locus2LG.txt
loci2LG6=$n/tests/metrics/${ID}${suffix6}/${ID}${suffix6}_locus2LG.txt
loci2LG7=$n/tests/metrics/${ID}${suffix7}/${ID}${suffix7}_locus2LG.txt

# all maps have the same number of line, ie the same markers in the same order
# adding marker to LG (eg JoinSingles2All) or removing markers from LG 
# only mean setting marker LG number : 0 to remove marker from LG or N to add marker to LGN
# so we can always use the same file to associate marker position in file (ie line number) and marker name 
# this file is created from data.call which was used by lepmap3 initial command (SeparateChromosome)
snp_name=$n/snp_nb2ID

options="data=$data_call lodLimit=$lod numThreads=64 distortionLod=1"

# 1) refine : => map1
if [ ! -e $map1 ]
then
    echo "lep-map3.sh SeparateChromosomes2 $options sizeLimit=$size phasedData=1 renameLGs=0 map=$map0 > $map1 2> $trace1"
    lep-map3.sh SeparateChromosomes2 $options sizeLimit=$size phasedData=1 renameLGs=0 map=$map0 > $map1 2> $trace1
else
    echo OK map1 $map1
fi

# 2) add single : map1 => map2
if [ ! -e $map2 ]
then
    echo "lep-map3.sh JoinSingles2All $options iterate=1 map=$map1 > $map2 2> $trace2"
    lep-map3.sh JoinSingles2All $options iterate=1 map=$map1 > $map2 2> $trace2
else
    echo OK map2 $map2
fi

# 3) refine : map2 => map3
if [ ! -e $map3 ]
then
    echo "lep-map3.sh SeparateChromosomes2 $options sizeLimit=$size phasedData=1 renameLGs=0 map=$map2 > $map3 2> $trace3"
    lep-map3.sh SeparateChromosomes2 $options sizeLimit=$size phasedData=1 renameLGs=0 map=$map2 > $map3 2> $trace3
else
    echo OK map3 $map3
fi

###################
# before clean, should run 6b_LG_metrics_v2.py to create loci2LG
if [ ! -e $loci2LG3 ]
then
    echo "./6b_LG_metrics_v2.py --in_data $data_call --in_map $map3 --out_dir $n/tests/metrics/${ID}${suffix3} > $n/tests/trace/6b_metrics_${ID}${suffix3} 2>&1"
    ./6b_LG_metrics_v2.py --in_data $data_call --in_map $map3 --out_dir $n/tests/metrics/${ID}${suffix3} > $n/tests/trace/6b_metrics_${ID}${suffix3} 2>&1
else
    echo OK loci2LG3 $loci2LG3
fi

# 4) clean : map3 => map4
if [ ! -e $map4 ]
then
    echo "./6e_LG_clean.py --loci2LG $loci2LG3 --snp_name $snp_name --in_map $map3 --out_map $map4  > $trace4 2>&1"
    ./6e_LG_clean.py --loci2LG $loci2LG3 --snp_name $snp_name --in_map $map3 --out_map $map4  > $trace4 2>&1
else
    echo OK map4 $map4
fi

# 5) add single : map4 => map5
if [ ! -e $map5 ]
then
    echo "lep-map3.sh JoinSingles2All $options iterate=1 map=$map4 > $map5 2> $trace5"
    lep-map3.sh JoinSingles2All $options iterate=1 map=$map4 > $map5 2> $trace5
else
    echo OK map5 $map5
fi


# 6) refine : map5 => map6
if [ ! -e $map6 ]
then
    echo "lep-map3.sh SeparateChromosomes2 $options sizeLimit=$size phasedData=1 renameLGs=0 map=$map5 > $map6 2> $trace6"
    lep-map3.sh SeparateChromosomes2 $options sizeLimit=$size phasedData=1 renameLGs=0 map=$map5 > $map6 2> $trace6
else
    echo OK map6 $map6
fi

# 7) clean : map6 => map7
# before clean, should run 6b_LG_metrics_v2.py to create loci2LG
if [ ! -e $loci2LG6 ]
then
    echo "./6b_LG_metrics_v2.py --in_data $data_call --in_map $map6 --out_dir $n/tests/metrics/${ID}${suffix6} > $n/tests/trace/6b_metrics_${ID}${suffix6} 2>&1"
    ./6b_LG_metrics_v2.py --in_data $data_call --in_map $map6 --out_dir $n/tests/metrics/${ID}${suffix6} > $n/tests/trace/6b_metrics_${ID}${suffix6} 2>&1
else
    echo OK loci2LG6 $loci2LG6
fi

if [ ! -e $map7 ]
then
    echo "./6e_LG_clean.py --loci2LG $loci2LG6 --snp_name $snp_name --in_map $map6 --out_map $map7  > $trace7 2>&1"
    ./6e_LG_clean.py --loci2LG $loci2LG6 --snp_name $snp_name --in_map $map6 --out_map $map7  > $trace7 2>&1
else
    echo OK map7 $map7
fi

# JoinSingles2All map (LG list) + data_call => map.txt (LG list) ================
#         map=map_file       Initial LG map file. Typically generated by SeparateChromosomes2, SeparateIdenticals or JoinSingles2*.
#         lodLimit=NUM       LOD score limit [10.0]
#         distortionLod=1    Use segregation distortion aware LOD scores (JoinSingles2All only) [not set]
#         iterate=1          Iterate single joining until no markers can be added (JoinSingles2All only) [not set]
#                            (iterating is much faster than running JoinSingles2All multiple times)
#         betweenSameType=1  Only compute LOD scores between identically informative markers (applicable to single family data and Join...Identicals)
#                            Also one has to specify 3 LOD limits (paternal, maternal and both) in this case

