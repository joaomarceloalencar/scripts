#!/bin/bash

aws ec2 describe-instances | jq '.Reservations[].Instances[] | .InstanceId, .PrivateIpAddress' | sed 's/\"//g' > instance.info

declare -a vet
i=0
for v in `cat instance.info`
do
   vet[$i]=$v 
   i=$(($i+1))
done

# echo ${vet[@]}


size=$((${#vet[@]} - 1))
for j in `seq 0 2 $size`
do
   printf "Instância: %s, IP Local: %s \n" ${vet[j]} ${vet[$(($j+1))]}
done

# echo $j

rm instance.info 
