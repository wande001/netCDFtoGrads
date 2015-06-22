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
python calcCorrelations.py 2 2 24 4 
python calcCorrelations.py 3 2 24 6 
python calcCorrelations.py 4 2 24 8 
python calcCorrelations.py 5 2 24 10 
python calcCorrelations.py 6 2 24 12 
python calcCorrelations.py 7 2 24 14 
python calcCorrelations.py 8 2 24 16 
python calcCorrelations.py 9 2 24 18 
python calcCorrelations.py 10 2 24 20 
python calcCorrelations.py 11 2 24 22 
python calcCorrelations.py 12 2 24 24 
