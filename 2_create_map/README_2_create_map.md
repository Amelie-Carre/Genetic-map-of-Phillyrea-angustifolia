# Step 2 Create genetic map using Lep-MAP3

## List of tools
- Lep-MAP3 (v. 0.2)
- bowtie2 version 2.4.1
- samtools 1.3.1

## Orig data
- list_parents, list_progeny and phen_trait_sex_SI (collect from step 1 (stacks)

## Creates folders for orig data, analysis results and copy orig data

    mkdir info
    for i in list_parents list_progeny phen_trait_sex_SI; do cp ../1_markers/res_v1/info/$i info ; done
    mkdir sn2; mkdir sn2/trace

## Align reads on markers catalog

Create folders

    mkdir sn2/data sn2/bam

Copy reference fasta from stacks markers catalog, index reference

    cp ../1_create_mk/res_v1/sn2/clean_catalog.fasta sn2/data/catalog.fasta
    bowtie2-build -f sn2/catalog.fasta sn2/catalog

Create symbolic link to raw reads :

    ln -s ../1_create_markers/reads/samples_pairs reads

Run alignment

    nohup ./01_aln_samples.sh sn2 info/list_parents info/list_progeny > sn2/trace/01_aln_samples 2>&1 &


## Create data.call input file for Lep-MAP3 with markers and "marker-coded" phenotypes 

### list_parents + list_progeny => sorted_bams, mapping.txt
Create sorted_bams file and mapping.txt file from list_parents + list_progeny

    ./02_mk_sorted_bams_and_mapping.py --in_parents info/list_parents --in_progeny info/list_progeny --bams_dir sn2/bam --out_mapping mapping.txt --out_bams sn2/sorted_bams > sn2/trace/02_mk_sorted_bams_and_mapping


### list_parents + list_progeny + phenotype => ped.txt phen.txt 
Create pedigrees file ped.txt and posterior for phenotype markers : post_phen. 
The input of ParentCall2 consists of genotype likelihoods (posteriors) for each 10 possible SNP genotypes AA, AC, AG, AT, CC, CG, CT, GG, GT and TT. We choose to code homozygote phenotype as "1 0 0 0 0 0 0 0 0 0", heterozygote as "0 1 0 0 0 0 0 0 0 0" and unknown as "1 1 1 1 1 1 1 1 1 1".

    ./03_mk_ped_phen.py --in_parents info/list_parents --in_progeny info/list_progeny --in_trait info/phen_trait_sex_SI --out_ped sn2/ped.txt --out_phen sn2/post_phen > sn2/trace/03_mk_ped_phen

### ped + post_phen => phen.call
Run ParentCall on phenotype markers

    lep-map3.sh ParentCall2 data=sn2/ped.txt posteriorFile=sn2/post_phen removeNonInformative=1 > sn2/phens.call 2> sn2/trace/04_ParentCall2_on_phen


### Convert bams to mpileup : SAMPLES.bams => all.mpileup1 
    nohup samtools mpileup -A -q 10 -Q 10 -s $(cat sn2/sorted_bams) > sn2/all.mpileup1 2> sn2/trace/05_mk_all.mpileup1 &


### mpileup filter 1 : remove markers with more than 30% of ind with cover < 5 reads : all.mpileup1 => all.mpileup2

Create a local version of lepmap3 pileupParser2.awk program with modified parameters

    sed -e 's/limit1 = 3/limit1 = 5/' < /PATH_TO_Lep-MAP3_TOOL/tools/pileupParser2.awk > 06_pileupParser2_EEP.awk
    
Run this modified version

    nohup awk -f 06_pileupParser2_EEP.awk < sn2/all.mpileup1 > sn2/all.mpileup2 2> sn2/trace/06_mk_all.mpileup2 &


### mpileup filter 2 : set 'unknown genotype' if cover < 5 reads : all.mpileup2 => all.mpileup3

Previous filter skip markers with more than 30% samples having cover < 5 reads. So we still have markers, with some genotypes having cover < 5 reads in less than 30% samples. This second filter will keep all markers, but will modify genotypes to unknown when cover is less than 5 reads. 

    ./07_filter_geno.py --min_cov 5 sn2/all.mpileup2 sn2/all.mpileup3 > sn2/trace/07_mk_all.mpileup3


### convert mpileup => post : all.mpileup3 => markers.post

    nohup awk -f /PATH_TO_Lep-MAP3/pileup2posterior.awk < sn2/all.mpileup3 > sn2/markers.post 2> sn2/trace/08_markers.post &


### Convert pedigree + markers.post => markers.call

    nohup lep-map3.sh ParentCall2 data=sn2/ped.txt posteriorFile=sn2/markers.post removeNonInformative=1 > sn2/markers.call 2> sn2/trace/09_ParentCall2_on_mk &


### Combine phens.call and markers.call ==> data.call_tmp
Concat phens.call and markers.call

    cat sn2/phens.call > sn2/data.call_tmp
    
skip 7 header lines

    tail -n +8 sn2/markers.call >> sn2/data.call_tmp
    

### Filter distorted markers (markers segregating in a non-Mendelian fashion) : data.call_tmp => data.call

    lep-map3.sh Filtering2 data=sn2/data.call_tmp removeNonInformative=1 dataTolerance=0.0000001 > sn2/data.call 2> sn2/trace/11_filter_data_call


### Associate line number to snp : data_call ==> snp_nb2ID
All maps have the same number of line, ie the same markers in the same order.
Adding marker to LG (eg JoinSingles2All) or removing markers from LG means only setting marker LG number 0 (to remove marker from LG) or N (to add marker to LGN). So we can always use the same file to associate maker position in file (ie line number) and marker name. This file is created from data.call which was used by Lep-MAP3 initial command (SeparateChromosome). This file is used in check_all.sh and 8b_map_recode.py.

    cut -f 1,2 < sn2/data.call | grep -v '#' | grep -v 'CHR' | cat -n | sed -e 's/ //g' > sn2/snp_nb2ID


## Create LGs using SeparateChromosomes2 :  pedigree + data.call => map.txt (= LG list)

Lep-MAP3 SeparateChromosome will be run with various values for 2 parameters : **lod** and **size**. Results files are named from N value for param lod and M value for param size : NAME.txt = map_l_N_s_M.txt

### Main strategy for scrip 6a_LG_create.py
For each pair or lod and size param : 

- create LG (lepmap3 SeparateChromsome) => NAME.txt
- compute metrics on LG (6b_LG_metrics_v2.py on NAME.txt)
- polish LG (6c_LG_polish_v2.sh : NAMEtxt => NAME**rsrcsr**.txt)
    - refine (lepmap3 SeparateChromosomes2 with an existing map) : NAME.txt => NAME**r**.txt
    - add singles (lepmap3 JoinSingles2All) : NAME**r**.txt => NAME**rs**.txt
    - refine (lepmap3 SeparateChromosomes2 with an existing map) : NAME**rs**.txt => NAME**rsr**.txt
    - clean (6e_LG_clean.py) : NAME**rsr**.txt => NAME**rsrc**.txt
    - add singles (lepmap3 JoinSingles2All) : NAME**rsrc**.txt => NAME**rsrcs**.txt
    - refine (lepmap3 SeparateChromosomes2 with an existing map) : NAME**rsrcs**.txt => NAME**rsrcsr**.txt
- compute metrics (6b_LG_metrics_v2.py on NAME**rsrcsr**.txt)

### Run script to create LGs 

    mkdir sn2/tests
    mkdir sn2/tests/trace
    mkdir sn2/tests/metrics
    nohup ./6a_LG_create.py --name sn2 --lod 20:30:1 --size 250:250:50 -v > sn2/trace/6a_map_l_20-30_s_250 2>&1 &

### Collect summary count and statistics

    ./6f_summary_res.py --name sn2 --lod 20:30:1 --size 250:250:50 > summary.csv
    ./6d_LG_stat.py --maps sn2/tests/map_l_27_s_250.txt

Results : best map 

    sn2/tests/map_l_27_s_250.txt : 24 LGs, 4 pheno mapped, 15,247 mk mapped (89.18%), ~ 635 mk per LG, 1,849 mk single, 17,096 tot mk


### Compare maps (2 genetics maps or 1 genetic and one physical map)
??? SHOULD remove comparison with first genetic map version
mkdir sn2/tests/cmp_map

sh 8f_cmp_map_summary.sh 

8e_cmp_map.sh utilise 

- 8d_cmp_maps_v2.py pour comparer 2 cartes genetiques (ie les nouvelles cartes avec l'ancienne nommée MSE)
- 8d_cmp_map_asm_v3.py pour comparer 1 carte génétique et 1 carte physique (ie le snouvelles cartes avec l'olivier)
La comparaison est faite dans les 2 sens map1 => map2 et map2 => map1

Les résultats sont dans sn2/tests/cmp_map/MAP1-MAP2.txt

8f_cmp_map_summary.sh collecte les résumé des comparaisos pour toutes les cartes. Les résulatst sont dans : sn2/tests/cmp_cmp/

- summary_check_MSE.csv
- summary_check_Oeu.csv
- summary_compare_MSE.csv
- summary_compare_Oeu.csv

## Merge LG20 et LG23 which are 2 parts of Oeu18

    sh merge_LG18.sh > sn2/trace/merge_LG18 2>&1

Output : map_OKsrc.txt

Result : OK no more markers in LG23 and more markers in LG20. Others LG are unchanged.

## Order markers in each LG using Lep-MAP3 OrderMarkers2 map : (LG list) + data.call => map (cM)

Run ordermarker 3 times with option sexAveraged 0 then 1. (warning, now LG23 has no markers)

ln -s map_OKsrc.txt sn2/tests/final.txt


    nohup ./7a_order_mk_v2.sh map_OKsrc > sn2/trace/7a_om_map_final 2>&1 & 

Results : final_map_OKsrc_LG_{1-24}_{0,1}_{1-3}.txt


Check scores

    grep '^logL =' sn2/trace/7a_om_map_final_map_OKsrc_LG_*_*_* > sn2/trace/7a_om_scores_map_final

Collect best map

    ./7a_get_best_maps.py --map map_OKsrc > sn2/trace/7a_get_best_maps

Result : final_best_map_OKsrc_LG_[1-24]_[01].txt

Concat all LG for each sex. 
LG23 will be ignored since 7a_get_best_maps.py didn't create result file for it.

    cat sn2/final_best_map_OKsrc_LG_*_0.txt > sn2/final_best_map_OKsrc_0.txt 
    cat sn2/final_best_map_OKsrc_LG_*_1.txt > sn2/final_best_map_OKsrc_1.txt 


## Reformat maps

### Concat all LG, recode markers ID, recode LG ID, create gmap format

- Create gmap format used in circos scripts + recode LG ID to use Oeu number.
- Manually create renum file : format = 1 line per LG, 2 cols LG_num:Oeu_num.
- Use sn2/tests/cmp_map/map_OKsrc-Oeu.txt to find corresponding Oeu chrom
- gmap format : mk_name,LG,male_pos,female_pos
- For option sexAverage=1, male_pos = female_pos = average_pos

    ./7b_format_gmap.py --renum_LG renum.txt --recode_mk sn2/snp_nb2ID --in_basename sn2/final_best_map_OKsrc_LG --in_sex 0 --out_map sn2/final_best_map_OKsrc_0.gmap -v > sn2/trace/       7b_format_gmap_sex0
    ./7b_format_gmap.py --renum_LG renum.txt --recode_mk sn2/snp_nb2ID --in_basename sn2/final_best_map_OKsrc_LG --in_sex 1 --out_map sn2/final_best_map_OKsrc_1.gmap -v  > sn2/trace/7b_format_gmap_sex1

## From gmap format, create files gmap_locus (warning if 2 snps for a same locus have different pos)

    ./8g_snpmap2locusmap_v2.py --in_map sn2/final_best_map_OKsrc_0.gmap --out_map sn2/final_best_map_OKsrc_0.gmap_locus > sn2/trace/8g_snpmap2locus_map_v2_sex_0
    ./8g_snpmap2locusmap_v2.py --in_map sn2/final_best_map_OKsrc_1.gmap --out_map sn2/final_best_map_OKsrc_1.gmap_locus > sn2/trace/8g_snpmap2locus_map_v2_sex_1

Since circos only uses first col, create males and female maps

    cut -d ',' -f 3 < sn2/final_best_map_OKsrc_0.gmap_locus > tmp_3
    cut -d ',' -f 4 < sn2/final_best_map_OKsrc_0.gmap_locus > tmp_4
    cut -d ',' -f 1,2,3 < sn2/final_best_map_OKsrc_0.gmap_locus > tmp_123
    cut -d ',' -f 1,2,4 < sn2/final_best_map_OKsrc_0.gmap_locus > tmp_124
    paste -d ',' tmp_123 tmp_3 > sn2/final_best_map_OKsrc_M.gmap_locus
    paste -d ',' tmp_124 tmp_4 > sn2/final_best_map_OKsrc_F.gmap_locus


