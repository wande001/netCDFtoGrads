import netCDF4 as nc
import datetime

import numpy as np
import grads

# Global variables:
MV = 1e20
smallNumber = 1E-39
grads_exe = '/home/water2/niko/Programs/opengrads-2.1.a2.oga.1.princeton/opengrads'
grads_exe = '/home/niko/Programs/opengrads-2.1.a2.oga.1.princeton/opengrads'

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
        print startDay
        print lastDay
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
                                      longName = None):
    
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


def readGrads(gradsfile,gradsVarName, gradsTime):
  ga = grads.GrADS(Bin=grads_exe,Window=False,Echo=False)
  
  ga("open " + gradsfile)
  
  if gradsTime != None:
    ga("set t " + gradsTime)
        
  longitudes = ga.coords().lon
  latitudes = ga.coords().lat
  time = ga.coords().denv.tyme[0]
  
  data=ga.exp(gradsVarName)
  data.longitudes = longitudes
  data.latitudes = latitudes
  data.time = time
  del(ga)
  return(data)

