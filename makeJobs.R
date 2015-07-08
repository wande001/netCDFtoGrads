start = "#!/bin/bash
# parallel job using 48 cores. and runs for 4 hours (max)
#SBATCH -n 1   # node count
#SBATCH -t 23:59:59
# sends mail when process begins, and
# when it ends. Make sure you define your email
# address.
#SBATCH --mail-type=end
#SBATCH --mail-user=nwanders@princeton.edu

cd /tigress/nwanders/Scripts/Seasonal/netCDFtoGrads\n"

runs = list()

runs[[1]] ="python calcCorrelations.py 0 1 24 1 $lag $model $varName $ref $varRef"
runs[[2]] = "python calcCorrelations.py 1 2 24 2 $lag $model $varName $ref $varRef"
runs[[3]] = "python calcCorrelations.py 2 2 24 4 $lag $model $varName $ref $varRef"
runs[[4]] = "python calcCorrelations.py 3 2 24 6 $lag $model $varName $ref $varRef"
runs[[5]] = "python calcCorrelations.py 4 2 24 8 $lag $model $varName $ref $varRef"
runs[[6]] = "python calcCorrelations.py 5 2 24 10 $lag $model $varName $ref $varRef"
runs[[7]] = "python calcCorrelations.py 6 2 24 12 $lag $model $varName $ref $varRef"
runs[[8]] = "python calcCorrelations.py 7 2 24 14 $lag $model $varName $ref $varRef"
runs[[9]] = "python calcCorrelations.py 8 2 24 16 $lag $model $varName $ref $varRef"
runs[[10]] = "python calcCorrelations.py 9 2 24 18 $lag $model $varName $ref $varRef"
runs[[11]] = "python calcCorrelations.py 10 2 24 20 $lag $model $varName $ref $varRef"
runs[[12]] = "python calcCorrelations.py 11 2 24 22 $lag $model $varName $ref $varRef"
runs[[13]] = "python calcCorrelations.py 12 2 24 24 $lag $model $varName $ref $varRef"

modelS = c("CanCM3","CanCM4","FLOR")
varNameS = c("prlr", "prlr", "pr")
refS = c("PGF","CFS")
varRefS = "prec"
lagS = c(0:11)

jobDir = "../jobs/"

master=""

for(m in 1:length(modelS)){
  model = modelS[m]
  varName = varNameS[m]
  for(ref in refS){
    for(varRef in varRefS){
      for(lag in lagS){
        setting=paste("model=",model,"\n","varName=",varName,"\n","ref=",ref,"\n","varRef=",varRef,"\n","lag=",as.character(lag),"\n", sep="")
        write.table(start, paste(jobDir,model,"_",varName,"_",ref,"_",lag,".sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE)
        write.table(setting, paste(jobDir,model,"_",varName,"_",ref,"_",lag,".sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE, append=TRUE)
        write.table(runs[[1]], paste(jobDir,model,"_",varName,"_",ref,"_",lag,".sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE, append=TRUE)
        for(i in 2:(13-lag)){
        #for(i in 3:4){
          write.table(runs[[i]], paste(jobDir,model,"_",varName,"_",ref,"_",lag,".sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE, append=TRUE)
        }
        master = paste(master,"sbatch ", paste(jobDir,model,"_",varName,"_",ref,"_",lag,".sh\n",sep=""),sep="")
      }
    }
  }
}

write.table(master, paste(jobDir,"master.sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE)
