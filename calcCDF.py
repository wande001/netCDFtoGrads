from readNC import *
#from plotMatrix import *
from scipy.stats.stats import spearmanr
import sys

def returnCDF(dateInput, endDay, model, varName, lag, month = 0, ensNr = 1, dirLoc=""):
    deltaDay = lagToDateTime(endDay, lag, model).day - lagToDateTime(dateInput, lag, model).day + 1
    deltaYear = lagToDateTime(endDay, lag, model).year - lagToDateTime(dateInput, lag, model).year + 1
    data = np.zeros((deltaYear,deltaDay,ensNr,180,360))+np.nan
    print data.shape
    start = datetime.datetime.strptime(str(dateInput),'%Y-%m-%d')
    end = datetime.datetime.strptime(str(endDay),'%Y-%m-%d')
    lastEntry = 0
    m = start.month
    for y in range(start.year, end.year+1):
        tempStartDate = datetime.datetime.strptime(str(str(y)+"-"+str(m)+"-01"),'%Y-%m-%d')
        zero = ""
        if len(str(m)) < 2: zero = "0"
        zeroDay = ""
        if len(str(start.day)) < 2: zeroDay="0"
        startDate = str(tempStartDate.year)+"-"+zero+str(tempStartDate.month)+"-"+zeroDay+str(start.day)
        tempEnd = lagToDateTime(findMonthEnd(y, m, 31, model),11, model)
        if tempStartDate.year >= start.year and tempStartDate < (end - datetime.timedelta (days = 1)):
            zero = ""
            if len(str(m)) < 2: zero = "0"
            zero2 = ""
            if len(str(tempEnd.month)) < 2: zero2 = "0"
            tempEndDate = lagToDateTime(findMonthEnd(y,end.month,end.day, model), lag, model)
            #tempEndDate = lagToDateTime(str(y)+"-"+zero+str(m)+"-"+str(end.day), lag)
            zero = ""
            if len(str(tempEndDate.month)) < 2: zero = "0"
            startDateTime = lagToDateTime(startDate, lag, model)
            endDateTime = lagToDateTime(findMonthEnd(y,end.month,end.day, model), lag, model)
            addYear = 0
            print endDateTime.month
            print startDateTime.month
            if endDateTime.year < startDateTime.year: addYear = 1
            endDateTime = lagToDateTime(findMonthEnd(y+addYear,end.month,end.day, model), lag, model)
            print startDate
            print findMonthEnd(y,end.month,end.day, model)
            print lagToDateTime(findMonthEnd(y,end.month,end.day, model), lag, model)
            print lag
            print endDateTime
            print lagToDateTime(startDate, lag, model)
            if endDateTime.month < startDateTime.month and endDateTime.year == startDateTime.year: addYear = 1
            endDate = lagToDateStr(findMonthEnd(y+addYear, end.month, end.day, model), lag, model)
            #deltaDay = (datetime.datetime.strptime(endDate,'%Y-%m-%d')-datetime.datetime.strptime(lagToDateStr(startDate, lag, model),'%Y-%m-%d')).days + 1
            for ens in range(ensNr):
                if model == "FLOR":
                    zero = ""
                    if len(str(m)) < 2: zero = "0"
                    ncFile = dirLoc+varName+"_day_GFDL-FLORB01_FLORB01-P1-ECDA-v3.1-"+zero+str(m)+str(y)+"_r"+str(ens+1)+"i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc4"
                    print ncFile
                    print lagToDateStr(startDate, lag, model)
                    print endDate
                    if ens == 0:
                        temp = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)
                        tempData = np.zeros((deltaDay, ensNr, temp.shape[1], temp.shape[2]))
                        tempData[:,ens,:,:] = temp[0:deltaDay,:,:]
                    else:
                        tempData[:,ens,:,:] = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)[0:deltaDay,:,:]
                if model == "CanCM3":
                    zero = ""
                    if len(str(m)) < 2: zero = "0"
                    ncFile = dirLoc+varName+"_day_"+model+"_"+str(y)+zero+str(m)+"_r"+str(ens+1)+"i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc4"
                    print ncFile
                    print lagToDateStr(startDate, lag, model)
                    print endDate
                    if ens == 0:
                        temp = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)
                        tempData = np.zeros((deltaDay, ensNr, temp.shape[1], temp.shape[2]))
                        tempData[:,ens,:,:] = temp[0:deltaDay,:,:]
                    else:
                        tempData[:,ens,:,:] = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)[0:deltaDay,:,:]
                if model == "CanCM4":
                    zero = ""
                    if len(str(m)) < 2: zero = "0"
                    ncFile = dirLoc+varName+"_day_"+model+"_"+str(y)+zero+str(m)+"_r"+str(ens+1)+"i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc4"
                    print ncFile
                    print lagToDateStr(startDate, lag, model)
                    print endDate
                    if ens == 0:
                        temp = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)
                        tempData = np.zeros((deltaDay, ensNr, temp.shape[1], temp.shape[2]))
                        tempData[:,ens,:,:] = temp[0:deltaDay,:,:]
                    else:
                        tempData[:,ens,:,:] = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)[0:deltaDay,:,:]
                if model == "Weighted":
                    zero = ""
                    if len(str(m)) < 2: zero = "0"
                    ncFile = dirLoc+str(y)+zero+str(m)+"01_forecasts_CanCM3_CanCM4_FLOR.nc"
                    print ncFile
                    print lagToDateStr(startDate, lag, model)
                    print endDate
                    tempData = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)
                if model == "CCSM":
                    zero = ""
                    if len(str(m)) < 2: zero = "0"
                    ncFile = dirLoc+varName+"_day_CCSM4_"+str(y)+zero+str(m)+"01_r"+str(ens+1)+"i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc4"
                    print ncFile
                    print lagToDateStr(startDate, lag, model)
                    print endDate
                    if ens == 0:
                        tempData = np.zeros((deltaDay, ensNr, 180,360))+np.nan
                        try:
                            temp = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)
                            tempData[:,ens,:,:] = temp[0:deltaDay,:,:]
                        except:
                            pass
                    else:
                        try:
                            tempData[:,ens,:,:] = readNC(ncFile,varName, lagToDateStr(startDate, lag, model), endDay = endDate, model=model)[0:deltaDay,:,:]
                        except:
                            pass
            data[lastEntry,:,:,:,:] = tempData[0:deltaDay,:,:,:]
            lastEntry += 1
    return(data)

def readForcingCDF(ncFile, varName, dateInput, endDay, lag=0, model="PGF"):
    deltaDay = lagToDateTime(endDay, lag, model).day - lagToDateTime(dateInput, lag, model).day + 1
    deltaYear = lagToDateTime(endDay, lag, model).year - lagToDateTime(dateInput, lag, model).year + 1
    data = np.zeros((deltaYear,deltaDay,180,360))
    print data.shape
    start = datetime.datetime.strptime(str(dateInput),'%Y-%m-%d')
    end = datetime.datetime.strptime(str(endDay),'%Y-%m-%d')
    lastEntry = 0
    m = start.month
    for y in range(start.year, end.year+1):
        tempStartDate = datetime.datetime.strptime(str(str(y)+"-"+str(m)+"-01"),'%Y-%m-%d')
        zero = ""
        if len(str(m)) < 2: zero = "0"
        zeroDay = ""
        if len(str(start.day)) < 2: zeroDay="0"
        startDate = str(tempStartDate.year)+"-"+zero+str(tempStartDate.month)+"-"+zeroDay+str(start.day)
        tempEnd = datetime.datetime.strptime(str(str(y+1)+"-"+str(m)+"-01"),'%Y-%m-%d') - datetime.timedelta (days = 1)
        if tempStartDate >= start and tempStartDate < (end - datetime.timedelta (days = 1)):
            startDateTime = lagToDateTime(startDate, lag, model)
            endDateTime = lagToDateTime(findMonthEnd(y,end.month,end.day, model), lag, model)
            addYear = 0
            if endDateTime.year < startDateTime.year: addYear = 1
            endDateTime = lagToDateTime(findMonthEnd(y+addYear,end.month,end.day, model), lag, model)
            if endDateTime.month < startDateTime.month and endDateTime.year == startDateTime.year: addYear = 1
            endDate = lagToDateStr(findMonthEnd(y+addYear, end.month, end.day, model), lag, model)
            print lagToDateStr(startDate, lag, model)
            print endDate
            data[lastEntry,:,:,:] = readNC(ncFile, varName, lagToDateStr(startDate, lag, model), endDay=endDate, model="PGF")[0:deltaDay,:,:]
            lastEntry += 1
    return(data)


def createNetCDF(ncFileName, varName, varUnits, latitudes, longitudes,\
                                      percNr = 101, longName = None, loop=False):
    
    rootgrp= nc.Dataset(ncFileName,'w')
    
    #-create dimensions - time is unlimited, others are fixed
    rootgrp.createDimension('pctl',percNr)
    rootgrp.createDimension('time',None)
    rootgrp.createDimension('lat',len(latitudes))
    rootgrp.createDimension('lon',len(longitudes))
    
    per= rootgrp.createVariable('pctl','f4',('pctl',))
    per.long_name= 'percentile'
    per.units= '%'
    per.standard_name = 'percentile'

    date_time= rootgrp.createVariable('time','f4',('time',))
    date_time.standard_name= 'time'
    date_time.long_name= 'Days since 1901-01-01'
    
    date_time.units= 'Days since 1901-01-01' 
    date_time.calendar= 'standard'
    
    lat= rootgrp.createVariable('lat','f4',('lat',))
    lat.long_name= 'latitude'
    lat.units= 'degrees_north'
    lat.standard_name = 'latitude'
    
    lon= rootgrp.createVariable('lon','f4',('lon',))
    lon.standard_name= 'longitude'
    lon.long_name= 'longitude'
    lon.units= 'degrees_east'
    
    per[:] = range(percNr)
    lat[:]= latitudes
    lon[:]= longitudes
    
    if loop:
        for i in range(len(varName)):
            shortVarName = varName[i]
            longVarName  = varName[i]
            if longName != None: longVarName = longName
            var= rootgrp.createVariable(shortVarName,'f4',('time','lat','lon','pctl') ,fill_value=MV,zlib=False)
            var.standard_name = varName[i]
            var.long_name = longVarName
            var.units = varUnits[i]
    else:    
        shortVarName = varName
        longVarName  = varName
        if longName != None: longVarName = longName
        var= rootgrp.createVariable(shortVarName,'f4',('time','lat','lon','pctl') ,fill_value=MV,zlib=False)
        var.standard_name = varName
        var.long_name = longVarName
        var.units = varUnits
    rootgrp.sync()
    rootgrp.close()


def data2NetCDF(ncFile,varName,varField,timeStamp,posCnt = None):
  #-write data to netCDF
  rootgrp= nc.Dataset(ncFile,'a')    
  
  shortVarName= varName        
  
  date_time= rootgrp.variables['time']
  if posCnt == None: posCnt = len(date_time)
  
  date_time[posCnt]= nc.date2num(timeStamp,date_time.units,date_time.calendar)
  rootgrp.variables[shortVarName][posCnt,:,:,:]= (varField)
  
  rootgrp.sync()
  rootgrp.close()


step = int(sys.argv[2])
end = int(sys.argv[3])
month = int(sys.argv[4])
tempScale = int(sys.argv[1])
model = sys.argv[5]
varName = sys.argv[6]
lag=0

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
if model == "CCSM":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/CCSM/"
    ensNr = 10
    if varName == "tas":
        factor = 1.
    else:
        factor = 1.
if model == "Weighted":
    dirLoc = "/tigress/nwanders/Scripts/Seasonal/Weighted/"
    ensNr = 1
    if varName == "tas":
        factor = 1.
    else:
        factor = 1.
if model == "PGF" and varName == "prec":
    ncRef = "../refData/prec_PGF_PCR.nc4"
    factor = 1.
if model == "CFS" and varName == "prec":
    ncRef = "../refData/prec_CFS_PCR.nc4"
    factor = 1.
if model == "PGF" and varName == "tas":
    ncRef = "../refData/tas_PGF_PCR.nc4"
    factor = 1.
if model == "CFS" and varName == "tas":
    ncRef = "../refData/tas_CFS_PCR.nc4"
    factor = 1.


ncOutputFile = "../resultsNetCDF/"+model+"_"+varName+"_pctl.nc4"

startDays = np.tile(["01","16"],24)
endDays = np.tile(["15","31","15","28","15","31","15","30","15","31","15","30","15","31","15","31","15","30","15","31","15","30","15","31"],2)
inputMonth = np.tile(np.repeat(["01","02","03","04","05","06","07","08","09","10","11","12"],2),2)
inputYear = np.repeat(["2011","2012"],24)
varNames = ["prec"]
varUnits = "mm/d"
createNetCDF(ncOutputFile, varName, varUnits, np.arange(89.5,-90,-1), np.arange(-179.5,180), loop=False)
posCount = 0

for event in range(0,end,step):
    dateInput = "1981-"+inputMonth[event]+"-"+startDays[event]
    endDay = inputYear[event+month-1]+"-"+inputMonth[event+month-1]+"-"+endDays[event+month-1]
    print dateInput
    print endDay
    
    if model == "CanCM3" or model == "CanCM4" or model == "FLOR" or model =="CCSM":
       data = returnCDF(dateInput, endDay, model, varName, lag, dirLoc = dirLoc, ensNr = ensNr) * factor
       numObs = data.shape[0] * data.shape[1] * data.shape[2]
       data = data.reshape(numObs, 180, 360)
       sel = np.isnan(data[:,1,1]) == False
       print sel
       data = data[sel,:,:]

    if model == "PGF" or model == "CFS" or model == "Weighted":
       data = readForcingCDF(ncRef, varName, dateInput, endDay=endDay, lag=lag, model=model) * factor
       numObs = data.shape[0] * data.shape[1]
       data = data.reshape(numObs, 180, 360)

    out = np.zeros((180, 360,101))

    if data.shape[0] != 0:
      for i in range(101):
        print i
        out[:,:,i] = np.percentile(data, float(i), axis=0)

    data2NetCDF(ncOutputFile, varName, out, lagToDateTime(dateInput, 0, model), posCnt = posCount)
    posCount += 1
    filecache = None
    del(data)
    del(out)

#corMap[signMap > 0.05] = 0.0

#plotMatrix(corMap)
#plotMatrix(signMap)

#createNetCDF("corMap.nc", "Cor", "Spearman", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", corMap, lagToDateTime(dateInput, lag))

#createNetCDF("signMap.nc", "Sign", "Significance level", range(-90,90), range(0,360))
#data2NetCDF("corMap.nc", "Cor", signMap, lagToDateTime(dateInput, lag))

#plotLine(dataPGF[:,100,100], NMME[:,100,100])
