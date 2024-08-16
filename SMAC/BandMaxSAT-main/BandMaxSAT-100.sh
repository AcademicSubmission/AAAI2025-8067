#!/bin/bash

# Set arguments first
for argument in "$@"
do
    key=$(echo $argument | cut -f1 -d=)
    value=$(echo $argument | cut -f2 -d=)

    if [[ $key == *"--"* ]]; then
        v="${key/--/}"
        declare $v="${value}"
    fi
done

# We simply set the cost to our parameter
EXE=./BandMaxSAT-best-f
cost=$($EXE $instance 666 -cpu_time 100 -bms_num $bms_num  -lambda_ $lambda_ -gamma $gamma -armnum $armnum -backward_step $backward_step)

echo "cost=$cost"