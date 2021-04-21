# Step 1 Create markers using stacks (version v2.3e)

## Dispatch reads from libraries and create reads per sample
Write 2 bash script which will create fastq files for each sample
> ./1a_mk_assign_script.py --config config_v1.yaml

Result : 2 scripts v1_dispatch.sh et v1_concat.sh

run dispatch script for each of 26 libraries
this will dispatch reads of each library and create per library samples file
> sh v1_dispatch.sh

Results : 
- NO_BACKUP/v1/lib/LIBRARY/SAMPLE{.1.fq.gz, .2.fq.gz, .rem.1.fq.gz, .rem.2.fq.gz}
- NO_BACKUP/v1/log/process_radtag_LIBRARY
- NO_BACKUP/v1/barcodes/LIBRARY

when dispatch is done, run second step to group all reads per sample (a sample can be present in more than one lib)

forward and reverse parts of the reads are treated as unrelated reads (as if we only have simple end)
> sh v1_concat.sh

Results : 
- NO_BACKUP/v1/samples/SAMPLE.fq.gz
- NO_BACKUP/v1/log/mk_se_SAMPLE

forward and reverse parts of the reads are treated as paired end
> sh 1d_concat_pairs.sh

Result : NO_BACKUP/v1/samples_pairs/SAMPLE{.1.fq.gz, .2.fq.gz}

Collect counts per lib and per sample
> ./1b_mk_summary.py --config config_v1.yaml -v

Result : NO_BACKUP/v1/summary_v1.yaml, NO_BACKUP/v1/summary_v1.xls

## run stacks pipeline with various parameters
### stacks protocole summary
1. create stacks for parents and progeny using stacks/ustacks
  - option **m** : Minimum depth of coverage required to create a stack (default 3) ⇒ 3
  - option **M** : Maximum distance (in nucleotides) allowed between stacks (default 2) ⇒ = 2, 3, 4
2. create catalog from parents's stacks using stccks/cstacks
   - option **n** : number of mismatches allowed between sample tags when generating the catalog (default 0). ⇒  same value as **M**
3. create genotypes for parents adn progeny from catalog and each sample stacks usung stacks/sstacks
4. create bam files for parents and progeny using stacks/tsv2bam
5. Re-assemble loci, create final catalog and new bam for parents and progeny using gstacks/gstacks
  lepmap3 will use these new bams, so we could stop here
  step 6 will enable to count loci and snps per loci in order to have statistics used in Rochette protocole to choose best value for n option
6. create haplotypes, loci … using stacks/population (option -R/--min-samples-overall [float]: minimum percentage of individuals across populations required to process a locus. = 0.45)

Final results :
- markers catalog (markers will be blasted to Ole genome in order to get syntheny between Pang genetic map and Ole physical map)
- per sample alignment file on this catalog (alignment files will be used by lepmap3 to build genetic map)

### Use protocol from Rochette 2017 to choose best 'n' param
- **M** controls the number of mismatches allowed between the two alleles of a heterozygote sample
- **n** controls the number of mismatches allowed between any two alleles of the population.
- **m** controls the number of identical reads required to initiate a new putative allele.
we tested param
- M : 2, 3, 4
- n = M
- m = 3

input file : phenotypes_2019-06-05.csv : phenotype file fo each sample with library name and barcode data

Create folders

> mkdir res_v1 ; mkdir res_v1/info

> for n in 2 3 4 ; do mkdir res_v1/sn$n; done

create file lists for samples and phenotypes
> ./2a_mk_pop_and_phen.py --in_phen phenotypes_2019-06-05.csv --out_dir res_v1/info -v

Results : 
- res_v1/info/phen_trait_sex
- res_v1/info/phen_trait_SI
- res_v1/info/phen_trait_sex_SI
- res_v1/info/phen_mk_sex
- res_v1/info/phen_mk_SI
- res_v1/info/samples_index
- res_v1/info/popmap_samples.tsv
- res_v1/info/popmap_progeny.tsv
- res_v1/info/popmap_parents_progeny.tsv
- res_v1/info/popmap_phen.tsv
- res_v1/info/list_parents
- res_v1/info/list_progeny

### creates scripts to run ustacks, cstacks, sstacks and tsv2bam on all samples with various n parameters
> sh 4a_run_stacks_per_sample.sh  2 3 4

Result : sh_stacks_per_samples_sn{2,3,4}.sh

### run theses scripts
> nohup sh sh_stacks_per_samples_sn2.sh > trace_sh_stacks_per_samples_sn2 2>&1 &
> 
> nohup sh sh_stacks_per_samples_sn3.sh > trace_sh_stacks_per_samples_sn3 2>&1 &
> 
> nohup sh sh_stacks_per_samples_sn4.sh > trace_sh_stacks_per_samples_sn4 2>&1 &


