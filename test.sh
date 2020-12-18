#!/bin/bash

cd sombrero
make
for i in {1..6}
do 
  mpirun -n 16 --oversubscribe ./sombrero/sombrero$i -l 16x16x16x16 -p 2x2x2x2
done
