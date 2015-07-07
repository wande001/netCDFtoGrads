from readNC import *
#from plotMatrix import *
from scipy.stats.stats import spearmanr
import sys

lag = int(sys.argv[5])
step = int(sys.argv[2])
end = int(sys.argv[3])
month = int(sys.argv[4])
tempScale = int(sys.argv[1])
model = sys.argv[6]
varName = sys.argv[7]
ref = sys.argv[8]
varNameRef = sys.argv[9]

if model == "CanCM3":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CanCM3/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        factor = 86400.*1000.
if model == "CanCM4":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CanCM4/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        factor = 86400.*1000.
if model == "FLOR":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/FLOR/"
    ensNr = 12
    if varName == "tas":
        factor = 1.
    else:
        factor = 86400.*1000.
if ref == "PGF" and varNameRef == "prec":
    ncRef = "../refData/prec_PGF.nc"
    refFactor = 1.
if ref == "CFS" and varNameRef == "prec":
    ncRef = "../refData/prec_CFS.nc"
    refFactor = 24.
if ref == "PGF" and varNameRef == "tas":
    ncRef = "../refData/tas_PGF.nc"
    refFactor = 1.
if ref == "CFS" and varNameRef == "tas":
    ncRef = "../refData/tas_CFS.nc"
    refFactor = 1.


ncOutputFile = "../resultsNetCDF/"+model+"_"+ref+"_"+varNameRef+"_tempScale_"+str(tempScale)+"_lag_"+str(lag)+".nc"

startDays = np.tile(["01","16"],24)
endDays = np.tile(["15","31","15","28","15","31","15","30","15","31","15","30","15","31","15","31","15","30","15","31","15","30","15","31"],2)
inputMonth = np.tile(np.repeat(["01","02","03","04","05","06","07","08","09","10","11","12"],2),2)
inputYear = np.repeat(["2011","2012"],24)
varNames = ["correlation_0","signif_0", "correlation_1","signif_1", "correlation_2","signif_2", "correlation_3","signif_3", "correlation_4","signif_4", "correlation_5","signif_5", "correlation_6","signif_6", "correlation_7","signif_7", "correlation_8","signif_8"]
varUnits = ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-"]
createNetCDF(ncOutputFile, varNames, varUnits, np.arange(-89.5,90), np.arange(0.5,360), loop=True)
posCount = 0

for event in range(0,end,step):
    dateInput = "1981-"+inputMonth[event]+"-"+startDays[event]
    endDay = inputYear[event+month-1]+"-"+inputMonth[event+month-1]+"-"+endDays[event+month-1]
    print dateInput
    print endDay
    
    NMME = returnSeasonalForecast(dateInput, endDay, model, varName, lag, dirLoc = dirLoc, ensNr = ensNr) * factor

    print lagToDateStr(dateInput, lag, model)
    print lagToDateStr(endDay, lag, model)
    dataPGF = readForcing(ncRef, varNameRef, dateInput, endDay=endDay, lag=lag, model=ref) * refFactor

    for space in range(9):
        print space
        spaceNMME = aggregateSpace(NMME, extent=space)
        spacePGF = aggregateSpace(dataPGF, extent=space)

        corMap = np.zeros((180,360))
        signMap = np.zeros((180,360))

        for i in range(180):
          for j in range(360):
            try:
                out = spearmanr(spacePGF[:,i,j], spaceNMME[:,i,j])
            except:
                out = np.ones(2)
                out[0] = 0
            corMap[i,j] = out[0]
            signMap[i,j] = out[1]

        data2NetCDF(ncOutputFile, "correlation_"+str(space), corMap, lagToDateTime(dateInput, 0, model), posCnt = posCount)
        data2NetCDF(ncOutputFile, "signif_"+str(space), signMap, lagToDateTime(dateInput, 0, model), posCnt = posCount)
    posCount += 1
    filecache = None
    del(NMME)
    del(dataPGF)

#corMap[signMap > 0.05] = 0.0

#plotMatrix(corMap)
#plotMatrix(signMap)

#createNetCDF("corMap.nc", "Cor", "Spearman", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", corMap, lagToDateTime(dateInput, lag))

#createNetCDF("signMap.nc", "Sign", "Significance level", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", signMap, lagToDateTime(dateInput, lag))

#plotLine(dataPGF[:,100,100], NMME[:,100,100])
