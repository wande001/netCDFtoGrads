#!/bin/bash
# parallel job using 48 cores. and runs for 4 hours (max)
#SBATCH -n 1   # node count
#SBATCH -t 23:59:00
# sends mail when process begins, and
# when it ends. Make sure you define your email
# address.
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=nwanders@princeton.edu

cd /tigress/nwanders/Scripts/Seasonal/netCDFtoGrads

python calcCorrelations.py 0 1 24 1 
python calcCorrelations.py 1 2 24 2 
python calcCorrelations.py 2 2 22 4 
python calcCorrelations.py 3 2 20 6 
python calcCorrelations.py 4 2 18 8 
python calcCorrelations.py 5 2 16 10 
python calcCorrelations.py 6 2 14 12 
python calcCorrelations.py 7 2 12 14 
python calcCorrelations.py 8 2 10 16 
python calcCorrelations.py 9 2 8 18 
python calcCorrelations.py 10 2 6 20 
python calcCorrelations.py 11 2 4 22 
python calcCorrelations.py 12 2 2 24 

