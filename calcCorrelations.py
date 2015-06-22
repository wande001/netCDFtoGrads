from readNC import *
#from plotMatrix import *
from scipy.stats.stats import spearmanr
import sys

lagTime = int(sys.argv[1])
step = int(sys.argv[2])
end = int(sys.argv[3])
month = int(sys.argv[4])

lag = 0

startDays = np.tile(["01","16"],12)
endDays = ["15","31","15","28","15","31","15","30","15","31","15","30","15","31","15","31","15","30","15","31","15","30","15","31"]
inputMonth = np.repeat(["01","02","03","04","05","06","07","08","09","10","11","12"],2)
varNames = ["correlation_0","signif_0", "correlation_1","signif_1", "correlation_2","signif_2", "correlation_3","signif_3", "correlation_4","signif_4", "correlation_5","signif_5", "correlation_6","signif_6", "correlation_7","signif_7", "correlation_8","signif_8"]
varUnits = ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-"]
createNetCDF("../FLOR_lag"+str(lagTime)+".nc", varNames, varUnits, np.arange(-89.5,90), np.arange(0.5,360), loop=True)

for event in range(0,end,step):
    dateInput = "1981-"+inputMonth[event]+"-"+startDays[event]
    endDay = "1987-"+inputMonth[event+month-1]+"-"+endDays[event+month-1]
    print dateInput
    print endDay
    
    model = "FLOR"
    varName = "pr"
    dirLoc = "../output1.NOAA-GFDL.FLORB-01.day.atmos/"
    
    NMME = returnSeasonalForecast(dateInput, endDay, model, varName, lag, dirLoc = dirLoc, ensNr = 12) * 86400.* 1000.

    ncFile = "../prec.nc"
    varName = "prec"

    dataPGF = readForcing(ncFile, varName, lagToDateStr(dateInput, lag), endDay=lagToDateStr(endDay, lag), lag=lag, model="PGF")

    for space in range(9):
        print space
        spaceNMME = aggregateSpace(NMME, extent=space)
        spacePGF = aggregateSpace(dataPGF, extent=space)

        corMap = np.zeros((180,360))
        signMap = np.zeros((180,360))

        for i in range(180):
          for j in range(360):
            out = spearmanr(spacePGF[:,i,j], spaceNMME[:,i,j])
            corMap[i,j] = out[0]
            signMap[i,j] = out[1]

        data2NetCDF("../FLOR_lag"+str(lagTime)+".nc", "correlation_"+str(space), corMap, lagToDateTime(dateInput, lag), posCnt=event)
        data2NetCDF("../FLOR_lag"+str(lagTime)+".nc", "signif_"+str(space), signMap, lagToDateTime(dateInput, lag), posCnt=event)

#corMap[signMap > 0.05] = 0.0

#plotMatrix(corMap)
#plotMatrix(signMap)

#createNetCDF("corMap.nc", "Cor", "Spearman", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", corMap, lagToDateTime(dateInput, lag))

#createNetCDF("signMap.nc", "Sign", "Significance level", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", signMap, lagToDateTime(dateInput, lag))

#plotLine(dataPGF[:,100,100], NMME[:,100,100])
