#!/bin/bash

ls -l | awk '{print $9}' > files.txt
N=1

while read line1; read line2

do
	echo 'Iter '$N
	echo $line1
	echo $line2
	N=$(($N+1))
done < 'files.txt'

