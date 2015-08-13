import datetime

def timeToStr(tempDate):
    zero = ""
    if len(str(tempDate.month)) < 2: zero = "0"
    zero2 = ""
    if len(str(tempDate.day)) < 2: zero2 = "0"
    newDate = str(tempDate.year) +"-"+ zero + str(tempDate.month) + "-" + zero2+str(tempDate.day)
    return(newDate)

beginYear = 1981
endYear = 2011
forcingInput = "/tigress/nwanders/Scripts/Seasonal/"
modelS = ["CanCM3","CanCM4", "FLOR"]
precVarNameS = ["prlr","prlr","pr"]
tempVarName = "tas"
refInput = "/tigress/nwanders/Scripts/Seasonal/refData/"
refModelS = ["PGF", "CFS"]
precRefVarName = "prec"
tempRefVarName = "tas"
precCorFactor = 1.0
pctlInput = "/tigress/nwanders/Scripts/Seasonal/resultsNetCDF/"

master = open("/tigress/nwanders/Scripts/Seasonal/jobs/CDFmaster.sh", "w")

for m in range(len(modelS)):
  model = modelS[m]
  precVarName = precVarNameS[m]
  for r in range(len(refModelS)):
    print r
    refModel = refModelS[r]
    for year in range(beginYear,endYear+1):
      for month in range(1,13):
        day = 1
        startTime = datetime.datetime(year, month, day)
        
        job = open("/tigress/nwanders/Scripts/Seasonal/jobs/CDF_"+model+"_"+refModel+"_"+timeToStr(startTime)+".sh", "w")
        job.writelines("#!/bin/bash\n")
        job.writelines("#SBATCH -n 1   # node count\n")
        job.writelines("#SBATCH -t 23:59:59\n")
        job.writelines("#SBATCH --mail-type=fail\n")
        job.writelines("#SBATCH --mail-user=nwanders@princeton.edu\n")
        job.writelines("cd /tigress/nwanders/Scripts/Seasonal/\n")
        job.writelines("python netCDFtoGrads/matchMeteoData.py "+model+" "+refModel+" "+str(year)+" "+str(month))
        job.close()
        
        master.writelines("sbatch /tigress/nwanders/Scripts/Seasonal/jobs/CDF_"+model+"_"+refModel+"_"+timeToStr(startTime)+".sh\n")

master.close()
