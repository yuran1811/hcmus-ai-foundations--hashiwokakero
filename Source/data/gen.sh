mkdir -p input output
mkdir -p input/3x3
mkdir -p input/5x5
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
    else
        inp="input-$i.txt"
    fi

	# touch "input/$inp"
	cp "input/__template/7x7.txt" "input/7x7/$inp"
    cp "input/__template/9x9.txt" "input/9x9/$inp"
    cp "input/__template/11x11.txt" "input/11x11/$inp"
    cp "input/__template/13x13.txt" "input/13x13/$inp"
    cp "input/__template/17x17.txt" "input/17x17/$inp"
    cp "input/__template/20x20.txt" "input/20x20/$inp"
done
