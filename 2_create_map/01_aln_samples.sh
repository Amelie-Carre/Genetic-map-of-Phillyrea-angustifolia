sn=$1
parents=`cat $2`
progeny=`cat $3`
samples="$parents $progeny"
ref=catalog

for sample in $samples
do
    echo $sample
    target=${sn}/bam/$sample.bam
    if [ ! -e $target ]
    then
	echo aln $sample
	zcat reads/$sample.[12].fq.gz | bowtie2 -x ${sn}/${ref} -U - --end-to-end --sensitive --threads 48 --no-unal 2> ${sn}/trace/aln_$sample | samtools view -S -b -u - | samtools sort - -o ${sn}/bam/$sample.bam
    fi
    target=${sn}bam/$sample.bam.bai
    if [ ! -e $target ]
    then
	echo index $sample
	samtools index ${sn}/bam/$sample.bam
    fi
done
echo END

