for n in $*
do
    M=$n
    ./4a_run_stacks_per_sample.py --top_dir res_v1 --name sn$n --parents list_parents --progeny list_progeny --sample_index samples_index --reads_dir NO_BACKUP/v1/samples -n $n -M $M -m 3 -p 64 --shell sh_stacks_per_samples_sn${n}.sh

done
