lod=27
size=250
data_call=sn2/data.call
map1=sn2/tests/map_OK.txt
map2=sn2/tests/map_OKs.txt
map3=sn2/tests/map_OKsr.txt
map4=sn2/tests/map_OKsrc.txt

echo "### reset markers on LG 23 ==> $map1"
sed -e 's/^23$/0/' < sn2/tests/map_l_27_s_250rsrcsrc.txt > $map1
echo "### add single ==> $map2"
lep-map3.sh JoinSingles2All data=$data_call lodLimit=$lod numThreads=64 distortionLod=1 iterate=1 map=$map1 > $map2
# refine
echo "### refine ==> $map3"
lep-map3.sh SeparateChromosomes2 data=$data_call lodLimit=$lod numThreads=64 distortionLod=1 sizeLimit=$size phasedData=1 renameLGs=0 map=$map2 > $map3
# clean
echo "### compute metrics on map_OKsr"
./6b_LG_metrics_v2.py --in_data $data_call --in_map $map3 --out_dir sn2/tests/metrics/map_OKsr
echo "### clean map_OKsr ==> $map4"
./6e_LG_clean.py --loci2LG sn2/tests/metrics/map_OKsr/map_OKsr_locus2LG.txt --snp_name sn2/snp_nb2ID --in_map $map3 --out_map $map4

echo "### compute metrics on finale map_OKsrc"
./6b_LG_metrics_v2.py --in_data $data_call --in_map $map4 --out_dir sn2/tests/metrics/map_OKsrc

echo "### compare final map $map4 to Oeu"
./8d_cmp_map_asm_v3.py --map1 sn2/tests/metrics/map_OKsrc/map_OKsrc_locus2LG.txt --blast ../res_v1/sn2/blast/sn2_Oeu.blast_ok > sn2/tests/cmp_map/map_OKsrc-Oeu.txt
