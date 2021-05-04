MAP=$1
# do not OrderMarker LG23 since it is empty
for chrom in 24 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1
do
    #for sex in 0
    for sex in 0 1
    do
	#for rep in 1
	for rep in 1 2 3
	do
	    name=final_${MAP}_LG_${chrom}_${sex}_${rep}
	    final_map=sn2/$name.txt
	    final_trace=sn2/trace/7a_om_map_$name
	    if [ ! -e $final_map ]
	    then
		echo lepmap3 chrom $chrom sex $sex rep $rep '=>' $name
		echo "lep-map3.sh OrderMarkers2 map=sn2/tests/${MAP}.txt data=sn2/data.call numThreads=64 chromosome=$chrom sexAveraged=$sex > $final_map 2> $final_trace"
		lep-map3.sh OrderMarkers2 map=sn2/tests/${MAP}.txt data=sn2/data.call numThreads=64 chromosome=$chrom sexAveraged=$sex > $final_map 2> $final_trace
	    else
		echo OK $final_map
	    fi
	done
    done
done
