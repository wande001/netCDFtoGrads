import netCDF4 as nc
import datetime

import numpy as np
import grads

# Global variables:
MV = 1e20
smallNumber = 1E-39
grads_exe = '/home/water1/niko/Programs/opengrads-2.1.a2.oga.1.princeton/opengrads'
grads_exe = '/tigress/nwanders/Programs/opengrads-2.1.a2.oga.1.princeton/opengrads'
#grads_exe = '/home/niko/Programs/opengrads-2.1.a2.oga.1.princeton/opengrads'

# file cache to minimize/reduce opening/closing files.  
filecache = dict()

def readNC(ncFile,varName, dateInput, latPoint = None, lonPoint = None, endDay = None, useDoy = None, LatitudeLongitude = False, specificFillValue = None, model = "NMME"):
    
    # Get netCDF file and variable name:
    if ncFile in filecache.keys():
        f = filecache[ncFile]
        print "Cached: ", ncFile
    else:
        f = nc.Dataset(ncFile)
        filecache[ncFile] = f
        print "New: ", ncFile
    
    #print ncFile
    #f = nc.Dataset(ncFile)  
    varName = str(varName)
    
    if LatitudeLongitude == True:
        try:
            f.variables['lat'] = f.variables['latitude']
            f.variables['lon'] = f.variables['longitude']
        except:
            pass
    if model == "NMME":
        orgDate = datetime.datetime(1850,2,2)
    if model == "PGF":
        orgDate = datetime.datetime(1901,1,1)
    if model == "FLOR":
        orgDate = datetime.datetime.strptime(str(dateInput),'%Y-%m-%d')
    date = dateInput
    if useDoy == "Yes": 
        idx = dateInput - 1
    elif endDay != "None":
        if isinstance(date, str) == True and isinstance(endDay, str) == True:
            startDay = datetime.datetime.strptime(str(date),'%Y-%m-%d')
            lastDay = datetime.datetime.strptime(str(endDay),'%Y-%m-%d')
        dateDif = datetime.datetime(startDay.year,startDay.month,startDay.day) - orgDate
        deltaDays = datetime.datetime(lastDay.year,lastDay.month,lastDay.day) - orgDate
        # time index (in the netCDF file)
        nctime = f.variables['time']  # A netCDF time variable object.
        if model == "FLOR":
            idx = range(int(np.where(nctime[:] == int(dateDif.days)+0.5)[0]), int(np.where(nctime[:] == int(deltaDays.days)+0.5)[0])+1)
        else:
            idx = range(int(np.where(nctime[:] == int(dateDif.days))[0]), int(np.where(nctime[:] == int(deltaDays.days))[0])+1)
    else:
        if isinstance(date, str) == True:
	  date = datetime.datetime.strptime(str(date),'%Y-%m-%d') 
        dateDif = datetime.datetime(date.year,date.month,date.day) - orgDate
        # time index (in the netCDF file)
        nctime = f.variables['time']  # A netCDF time variable object.
        idx = int(np.where(nctime[:] == int(dateDif.days))[0])
    
    outputData = f.variables[varName][idx,:,:]       # still original data
    
    f = None
    
    return(outputData)

def createNetCDF(ncFileName, varName, varUnits, latitudes, longitudes,\
                                      longName = None, loop=False):
    
    rootgrp= nc.Dataset(ncFileName,'w')
    
    #-create dimensions - time is unlimited, others are fixed
    rootgrp.createDimension('time',None)
    rootgrp.createDimension('lat',len(latitudes))
    rootgrp.createDimension('lon',len(longitudes))
    
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
    
    lat[:]= latitudes
    lon[:]= longitudes
    
    if loop:
        for i in range(len(varName)):
            shortVarName = varName[i]
            longVarName  = varName[i]
            if longName != None: longVarName = longName
            var= rootgrp.createVariable(shortVarName,'f4',('time','lat','lon',) ,fill_value=MV,zlib=False)
            var.standard_name = varName[i]
            var.long_name = longVarName
            var.units = varUnits[i]
    else:    
        shortVarName = varName
        longVarName  = varName
        if longName != None: longVarName = longName
        var= rootgrp.createVariable(shortVarName,'f4',('time','lat','lon',) ,fill_value=MV,zlib=False)
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
  rootgrp.variables[shortVarName][posCnt,:,:]= (varField)
  
  rootgrp.sync()
  rootgrp.close()


def readGrads(gradsfile,gradsVarName, gradsTime, lon=[0.5, 359.5], lat=[-89.5, 89.5]):
  ga = grads.GrADS(Bin=grads_exe,Window=False,Echo=False)
  
  ga("open " + gradsfile)
  
  if gradsTime != None:
    ga("set t " + gradsTime)
        
  ga("set lon "+ str(lon[0]) +" "+str(lon[1]))
  ga("set lat "+ str(lat[0]) +" "+str(lat[1]))
  longitudes = ga.coords().lon
  latitudes = ga.coords().lat
  time = ga.coords().denv.tyme[0]
  
  data=ga.exp(gradsVarName)
  data.longitudes = longitudes
  data.latitudes = latitudes
  data.time = time
  del(ga)
  return(data)

def findMonthEnd(year, month, day):
    if month + 1 <= 12:
        firstDay = datetime.datetime(year, month+1,1)
    else:
        firstDay = datetime.datetime(year+1, month-11,1)
    out =firstDay-datetime.timedelta (days = 1)
    if day > 25: day=31
    if out.day > day:
        out = datetime.datetime(year, month, day)
    return(out)

def lagToDateStr(date, lag):
    try:
        startDate = datetime.datetime.strptime(date,'%Y-%m-%d')
    except:
        startDate = date
    y = startDate.year
    m = startDate.month
    d = startDate.day
    if m+lag > 12:
        tempEndDate = findMonthEnd(y+1,m-12+lag,d)
        zero = ""
        if len(str(m-11+lag)) < 2: zero = "0"
        zero2 = ""
        if len(str(startDate.day)) < 2: zero2 = "0"
        newDate = str(tempEndDate.year) +"-"+ zero + str(tempEndDate.month) + "-" + zero2+str(tempEndDate.day)
    else:
        tempEndDate = findMonthEnd(y,m+lag,d)        
        zero = ""
        if len(str(m+lag)) < 2: zero = "0"
        zero2 = ""
        if len(str(startDate.day)) < 2: zero2 = "0"
        newDate = str(tempEndDate.year) +"-"+ zero + str(tempEndDate.month) + "-" + zero2+str(tempEndDate.day)
    return(newDate)


def lagToDateTime(date, lag):
    try:
        startDate = datetime.datetime.strptime(date,'%Y-%m-%d')
    except:
        startDate = date
    y = startDate.year
    m = startDate.month
    d = startDate.day
    if m+lag > 12:
        tempEndDate = findMonthEnd(y+1,m-12+lag,d)
    else:
        tempEndDate = findMonthEnd(y,m+lag,d)
    return(tempEndDate)


def returnSeasonalForecast(dateInput, endDay, model, varName, lag, ensNr = 1, dirLoc=""):
    deltaDay = lagToDateTime(endDay, lag).day - lagToDateTime(dateInput, lag).day + 1
    deltaYear = lagToDateTime(endDay, lag).year - lagToDateTime(dateInput, lag).year + 1
    
    data = np.zeros((deltaYear,180,360))
    
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
        if tempStartDate.year >= start.year and tempStartDate < (end - datetime.timedelta (days = 1)):
            zero = ""
            if len(str(m)) < 2: zero = "0"
            zero2 = ""
            if len(str(tempEnd.month)) < 2: zero2 = "0"
            tempEndDate = lagToDateTime(findMonthEnd(y,m,end.day), lag)
            #tempEndDate = lagToDateTime(str(y)+"-"+zero+str(m)+"-"+str(end.day), lag)
            zero = ""
            if len(str(tempEndDate.month)) < 2: zero = "0"
            endDate = lagToDateStr(findMonthEnd(y,m,end.day), lag)
            #endDate = lagToDateStr(findMonthEnd(str(y)+"-"+zero+str(m)+"-"+str(end.day)), lag)
            deltaDay = (datetime.datetime.strptime(endDate,'%Y-%m-%d')-datetime.datetime.strptime(lagToDateStr(startDate, lag),'%Y-%m-%d')).days + 1
            tempData = np.zeros((ensNr, deltaDay, 180,360))
            for ens in range(ensNr):
                ncFile = "prlr_day_"+model+"_"+str(y)+zero+str(m)+"_r1i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc4"
                if model == "FLOR":
                    zero = ""
                    if len(str(m)) < 2: zero = "0"
                    ncFile = dirLoc+"pr_day_GFDL-FLORB01_FLORB01-P1-ECDA-v3.1-"+zero+str(m)+str(y)+"_r"+str(ens+1)+"i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc"
                    print ncFile
                    print lagToDateStr(startDate, lag)
                    print endDate
                    tempData[ens,:,:,:] = readNC(ncFile,varName, lagToDateStr(startDate, lag), endDay = endDate, model=model)
            data[lastEntry,:,:] = aggregateTime(ensembleMean(tempData))
            lastEntry += 1
    return(data)


def aggregateTime(data, timeDimension = 0):
    outPut = data.sum(axis=timeDimension)
    return(outPut)

def ensembleMean(data, ensDimension = 0):
    outPut = data.mean(axis=ensDimension)
    return(outPut)

def aggregateSpace(data, extent = 0):
    if extent != 0:
        outPut = data
        dy = data.shape[1]
        dx = data.shape[2]
        largerData = np.zeros(np.add(data.shape, (0,extent*2,extent*2)))
        yLen = range(extent,(dy+extent))
        xLen = range(extent,(dx+extent))
        largerData[:,extent:(dy+extent), extent:(dx+extent)] = data
        largerData[:,yLen,0:extent] = data[:,:,dx-extent:dx]
        largerData[:,yLen,dx:(dx+extent)] = data[:,:,0:extent]
        largerData[:,0:extent,xLen] = data[:,dy-extent:dy,:]
        largerData[:,dy:(dy+extent),xLen] = data[:,0:extent,:]
        for x in range(-extent, extent+1):
            for y in range(-extent, extent+1):
                if x == 0 and y == 0:
                    pass
                else:
                    outPut += largerData[:,extent+y:dy+extent+y, extent+x:dx+extent+x]
        return(outPut/(extent**2))
    else:
        return(data)

def readForcing(ncFile, varName, dateInput, endDay, lag=0, model="PGF"):
    deltaDay = lagToDateTime(endDay, lag).day - lagToDateTime(dateInput, lag).day + 1
    deltaYear = lagToDateTime(endDay, lag).year - lagToDateTime(dateInput, lag).year + 1
    
    data = np.zeros((deltaYear,180,360))
    
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
        print startDate
        if tempStartDate >= start and tempStartDate < (end - datetime.timedelta (days = 1)):
            endDate = lagToDateStr(findMonthEnd(y,m,end.day), 0)
            print endDate
            data[lastEntry,:,:] = aggregateTime(readNC(ncFile, varName, lagToDateStr(startDate, 0), endDay=endDate, model="PGF"))
            lastEntry += 1
    return(data)
