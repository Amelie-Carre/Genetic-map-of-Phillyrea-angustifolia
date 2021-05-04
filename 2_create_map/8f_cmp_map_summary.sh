for a in MSE Oeu
do
    for b in check compare
    do
	res=sn2/tests/cmp_map/summary_${b}_${a}.csv
	echo $a $b $res
	grep "summary $b" sn2/tests/cmp_map/*${a}.txt | sed -e 's/:/\t/' > $res
	todos $res
    done
done
