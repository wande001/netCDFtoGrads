from readNC import *
#from plotMatrix import *
from scipy.stats.stats import percentileofscore
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
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CanCM3_org/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        factor = 1.

if model == "CanCM4":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CanCM4_org/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        factor = 1.

if model == "FLOR":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/FLOR_org/"
    ensNr = 12
    if varName == "tas":
        factor = 1.
    else:
        factor = 1.

if ref == "PGF" and varNameRef == "prec":
    ncRef = "../refData/prec_PGF_PCR.nc4"
    refFactor = 1.

if ref == "CFS" and varNameRef == "prec":
    ncRef = "../refData/prec_CFS_PCR.nc4"
    refFactor = 1.

if ref == "PGF" and varNameRef == "tas":
    ncRef = "../refData/tas_PGF_PCR.nc4"
    refFactor = 1.

if ref == "CFS" and varNameRef == "tas":
    ncRef = "../refData/tas_CFS_PCR.nc4"
    refFactor = 1.


ncOutputFile = "../resultsNetCDF/"+model+"_"+ref+"_"+varNameRef+"_tempScale_"+str(tempScale)+"_lag_"+str(lag)+"_quant.nc4"

startDays = np.tile(["01","16"],24)
endDays = np.tile(["15","31","15","28","15","31","15","30","15","31","15","30","15","31","15","31","15","30","15","31","15","30","15","31"],2)
inputMonth = np.tile(np.repeat(["01","02","03","04","05","06","07","08","09","10","11","12"],2),2)
inputYear = np.repeat(["2011","2012"],24)
varNames = ["uncorrected", "corrected"]
varUnits = ["-","-"]

yearStep = 12
ncYears = np.repeat(range(1981,2012),12)
ncMonths = np.tile(["01","02","03","04","05","06","07","08","09","10","11","12"],31)
ncDays = np.tile(["01"],12*31)
if tempScale == 0:
  yearStep = 24
  ncYears = np.repeat(range(1981,2012),24)
  ncMonths = np.tile(np.repeat(["01","02","03","04","05","06","07","08","09","10","11","12"],2),31)
  ncDays = np.tile(["01","16"],12*31)

yearS = int(inputYear[0]) - 1981 + 1
unCorMap = np.zeros((yearS*yearStep,180,360))
corMap = np.zeros((yearS*yearStep,180,360))

dayStep = 0
for event in range(0,end,step):
    dateInput = "1981-"+inputMonth[event]+"-"+startDays[event]
    endDay = inputYear[event+month-1]+"-"+inputMonth[event+month-1]+"-"+endDays[event+month-1]
    print dateInput
    print endDay
    NMME = returnSeasonalEnsembleForecast(dateInput, endDay, model, varName, lag, dirLoc = dirLoc, ensNr = ensNr) * factor
    print lagToDateStr(dateInput, lag, model)
    print lagToDateStr(endDay, lag, model)
    dataPGF = readForcing(ncRef, varNameRef, dateInput, endDay=endDay, lag=lag, model=ref) * refFactor
    if event == 0:
      unCorMap = np.zeros((NMME.shape[0]*yearStep,180,360))
      corMap = np.zeros((NMME.shape[0]*yearStep,180,360))
    for year in range(yearS):
      sortCDF = np.sort(NMME[year,:,:,:], axis=0)
      corSortCDF = np.sort(NMME[year,:,:,:] - np.mean(np.mean(NMME[:,:,:,:], axis=0), axis=0))
      out = np.zeros((180,360))
      outBias = np.zeros((180,360))
      for n in range(ensNr):
        temp = dataPGF[year,:,:] > sortCDF[n,:,:]
        out[temp] = (n+1)/float(ensNr)
        temp = dataPGF[year,:,:] > corSortCDF[n,:,:]
        outBias[temp] = (n+1)/ensNr
      print unCorMap.shape
      print out.shape
      print year*yearStep+dayStep
      unCorMap[year*yearStep+dayStep,:,:] = out
      corMap[year*yearStep+dayStep,:,:] = outBias
    filecache = None
    dayStep += 1
    del(NMME)
    del(dataPGF)

createNetCDF(ncOutputFile, varNames, varUnits, np.arange(89.5,-90,-1), np.arange(-179.5,180), loop=True)
posCount = 0
for time in range(yearS*yearStep):
  ncDate = datetime.datetime(ncYears[time],int(ncMonths[time]),int(ncDays[time]))
  data2NetCDF(ncOutputFile, "uncorrected", unCorMap[time,:,:], ncDate, posCnt = posCount)
  data2NetCDF(ncOutputFile, "corrected", corMap[time,:,:], ncDate, posCnt = posCount)
  posCount += 1

#corMap[signMap > 0.05] = 0.0

#plotMatrix(corMap)
#plotMatrix(signMap)

#createNetCDF("corMap.nc", "Cor", "Spearman", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", corMap, lagToDateTime(dateInput, lag))

#createNetCDF("signMap.nc", "Sign", "Significance level", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", signMap, lagToDateTime(dateInput, lag))

#plotLine(dataPGF[:,100,100], NMME[:,100,100])
