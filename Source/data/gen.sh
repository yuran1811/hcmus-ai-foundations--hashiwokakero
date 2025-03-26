mkdir -p input output

for i in $(seq 0 1 10); do
    if [ $i -lt 10 ];
	then
        inp="input-0$i.txt"
        out="output-0$i.txt"
    else
        inp="input-$i.txt"
        out="output-$i.txt"
    fi

	touch "input/$inp" "output/$out"
done