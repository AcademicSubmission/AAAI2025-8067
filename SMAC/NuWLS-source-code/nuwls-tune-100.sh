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
EXE=./nuwls-100
cost=$($EXE $instance 666 -bms_num $bms_num  -hard_sp $hard_sp -soft_sp $soft_sp -soft_weight_threshold $soft_weight_threshold -h_inc $h_inc -s_inc $s_inc -coe $coe)

echo "cost=$cost"