mkdir -p input output
mkdir -p input/7x7
mkdir -p input/9x9
mkdir -p input/11x11
mkdir -p input/13x13
mkdir -p input/17x17
mkdir -p input/20x20

for i in $(seq 1 1 5); do
    if [ $i -lt 10 ];
	then
        inp="input-0$i.txt"
        out="output-0$i.txt"
    else
        inp="input-$i.txt"
        out="output-$i.txt"
    fi

	# touch "input/$inp" "output/$out"
	cp "input/7x7.txt" "input/7x7/$inp"
    cp "input/9x9.txt" "input/9x9/$inp"
    cp "input/11x11.txt" "input/11x11/$inp"
    cp "input/13x13.txt" "input/13x13/$inp"
    cp "input/17x17.txt" "input/17x17/$inp"
    cp "input/20x20.txt" "input/20x20/$inp"
done