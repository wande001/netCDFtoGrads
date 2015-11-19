from readNC import *
#from plotMatrix import *
from scipy.stats.stats import spearmanr
from scipy.optimize import nnls
import sys

def returnForecast(dateInput, endDay, model, varName, lag):
  if model == "CanCM3":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CanCM3/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        varName = "prlr"
        factor = 1000.
  if model == "CanCM4":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CanCM4/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        varName = "prlr"
        factor = 1000.
  if model == "FLOR":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/FLOR/"
    ensNr = 12
    if varName == "tas":
        factor = 1.
    else:
        varName = "pr"
        factor = 1000.
  if model == "CCSM":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CCSM/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        varName = "prec"
        factor = 1
  out, varData = returnSeasonalForecastFit(dateInput, endDay, model, varName, lag, dirLoc = dirLoc, ensNr = ensNr)        
  return(out*factor, varData*factor)

def calcEnsVar(covMatrix, coef):
  totalVar = 0
  for i in range(covMatrix.shape[0]):
    for j in range(covMatrix.shape[0]):
      totalVar += coef[i]*coef[j]*abs(covMatrix[i,j])
  return(totalVar)

varName = sys.argv[1]
ref = "PGF"
start = int(sys.argv[2])

startNum = start*2-2
varNameRef = varName
if ref == "PGF" and varNameRef == "prec":
    ncRef = "../refData/prec_PGF_PCR.nc4"
    refFactor = 1000.

if ref == "PGF" and varNameRef == "tas":
    ncRef = "../refData/tas_PGF_PCR.nc4"
    refFactor = 1.

ncOutputFile = "../resultsNetCDF/NNLS_weights_month_"+str(start)+"_var_"+varName+".nc4"

startDays = np.tile(["01","16"],24)
endDays = np.tile(["15","31","15","28","15","31","15","30","15","31","15","30","15","31","15","31","15","30","15","31","15","30","15","31"],2)
inputMonth = np.tile(np.repeat(["01","02","03","04","05","06","07","08","09","10","11","12"],2),2)
inputYear = np.repeat(["2011","2012"],24)
varNames = ["CanCM3","CanCM4","FLOR","var","CanCM3ref","CanCM4ref","FLORref","PGFref"]
varUnits = ["-","-","-","-","-","-","-","-"]
createNetCDF(ncOutputFile, varNames, varUnits, np.arange(89.5,-90,-1), np.arange(-179.5,180), loop=True)

posCount = 0

for lag in range(12):
  for event in range(startNum,startNum+2):
    month = 1
    dateInput = "1981-"+inputMonth[event]+"-"+startDays[event]
    endDay = inputYear[event+month-1]+"-"+inputMonth[event+month-1]+"-"+endDays[event+month-1]
    print dateInput
    print endDay
    
    ensCanCM3, varCanCM3 = returnForecast(dateInput, endDay, "CanCM3", varName, lag)
    ensCanCM4, varCanCM4 = returnForecast(dateInput, endDay, "CanCM4", varName, lag)
    ensFLOR, varFLOR = returnForecast(dateInput, endDay, "FLOR", varName, lag)
    newData = np.zeros((3, 180, 360))
    newVar = np.zeros((180, 360))
    
    dataPGF = readForcing(ncRef, varNameRef, dateInput, endDay=endDay, lag=lag, model=ref) * refFactor
    
    for i in range(180):
      print i
      for j in range(360):
        try:
            A = np.zeros((31,3))
            A[:,0] = ensCanCM3[:,i,j] - np.mean(ensCanCM3[:,i,j])
            A[:,1] = ensCanCM4[:,i,j] - np.mean(ensCanCM4[:,i,j])
            A[:,2] = ensFLOR[:,i,j] - np.mean(ensFLOR[:,i,j])
            covAll = np.cov(A, rowvar=0)
            covAll[0,0] = varCanCM3[i,j]
            covAll[1,1] = varCanCM4[i,j]
            covAll[2,2] = varFLOR[i,j]
            out = nnls(A[:,0:3], dataPGF[:,i,j]-np.mean(dataPGF[:,i,j]))[0]
            outVar = calcEnsVar(covAll[0:3,0:3], out)
            newData[:,i,j] = out[0:3]
            newVar[i,j] = outVar
        except:
            newData[:,i,j] = np.nan
            newVar[i,j] = np.nan
    data2NetCDF(ncOutputFile, "CanCM3", newData[0,:,:], lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "CanCM4", newData[1,:,:], lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "FLOR", newData[2,:,:], lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "var", newVar, lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "CanCM3ref", np.mean(ensCanCM3, axis=0), lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "CanCM4ref", np.mean(ensCanCM4, axis=0), lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "FLORref", np.mean(ensFLOR, axis=0), lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    data2NetCDF(ncOutputFile, "PGFref", np.mean(dataPGF, axis=0), lagToDateTime(dateInput, lag, "PGF"), posCnt = posCount)
    posCount += 1
    filecache = None
    del ensCanCM3
    del ensCanCM4
    del ensFLOR
    del dataPGF
    del varCanCM3
    del varCanCM4
    del varFLOR
