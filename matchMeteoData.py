import os
from pcraster.framework import *
import pcraster as pcr

import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import pcraster as pcr
import datetime
import sys

def createNetCDF(ncFileName, varName, varUnits, latitudes, longitudes,\
                                      longName = None, loop=False):
    
    rootgrp= nc.Dataset(ncFileName,'w',format='NETCDF4')
    
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
            var= rootgrp.createVariable(shortVarName,'f4',('time','lat','lon',) ,fill_value=MV,zlib=True)
            var.standard_name = varName[i]
            var.long_name = longVarName
            var.units = varUnits[i]
    else:    
        shortVarName = varName
        longVarName  = varName
        if longName != None: longVarName = longName
        var= rootgrp.createVariable(shortVarName,'f4',('time','lat','lon',) ,fill_value=MV,zlib=True)
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


# Global variables:
MV = 1e20
smallNumber = 1E-39

# file cache to minimize/reduce opening/closing files.  
filecache = dict()

def netcdf2PCRobjClone(ncFile,varName,dateInput,\
                       useDoy = None,
                       cloneMapFileName  = None,\
                       LatitudeLongitude = True,\
                       specificFillValue = None,\
                       allData = False):
    # 
    # EHS (19 APR 2013): To convert netCDF (tss) file to PCR file.
    # --- with clone checking
    #     Only works if cells are 'square'.
    #     Only works if cellsizeClone <= cellsizeInput
    # Get netCDF file and variable name:
    
    #~ print ncFile
        
    if ncFile in filecache.keys():
        f = filecache[ncFile]
        print "Cached: ", ncFile
    else:
        f = nc.Dataset(ncFile)
        filecache[ncFile] = f
        print "New: ", ncFile
    
    varName = str(varName)
    
    if LatitudeLongitude == True:
        try:
            f.variables['lat'] = f.variables['latitude']
            f.variables['lon'] = f.variables['longitude']
        except:
            pass
    
    if varName == "evapotranspiration":        
        try:
            f.variables['evapotranspiration'] = f.variables['referencePotET']
        except:
            pass
    
    # date
    date = dateInput
    if useDoy == "Yes": 
        idx = dateInput - 1
    else:
        if isinstance(date, str) == True: date = \
                        datetime.datetime.strptime(str(date),'%Y-%m-%d') 
        date = datetime.datetime(date.year,date.month,date.day)
        # time index (in the netCDF file)
        if useDoy == "month":
            idx = int(date.month) - 1
        else:
            nctime = f.variables['time']  # A netCDF time variable object.
            if useDoy == "yearly":\
                date = datetime.datetime(date.year,int(1),int(1))
            if useDoy == "monthly":\
                date = datetime.datetime(date.year,date.month,int(1))
            try:
                idx = nc.date2index(date, nctime, calendar = nctime.calendar, \
                                                  select='exact')
            except:                                  
                try:
                    idx = nc.date2index(date, nctime, calendar = nctime.calendar, \
                                                      select='before')
                    msg  = "\n"
                    msg += "WARNING related to the netcdf file: "+str(ncFile)+" ; variable: "+str(varName)+" !!!!!!"+"\n"
                    msg += "No "+str(dateInput)+" is available. The 'before' option is used while selecting netcdf time."
                    msg += "\n"
                except:
                    try:
                        idx = nc.date2index(date, nctime, calendar = nctime.calendar, \
                                                          select='after')
                        msg  = "\n"
                        msg += "WARNING related to the netcdf file: "+str(ncFile)+" ; variable: "+str(varName)+" !!!!!!"+"\n"
                        msg += "No "+str(dateInput)+" is available. The 'after' option is used while selecting netcdf time."
                        msg += "\n"
                    except:
                        idx = nc.date2index(date-datetime.timedelta(days=1), nctime, calendar = nctime.calendar, \
                                                          select='exact')
                        msg  = "\n"
                        msg += "WARNING related to the netcdf file: "+str(ncFile)+" ; variable: "+str(varName)+" !!!!!!"+"\n"
                        msg += "No "+str(dateInput)+" is available. The 'leapyear' option is used while selecting netcdf time."
                        msg += "\n"                                 
                print msg               
    idx = int(idx)
    if allData:
      cropData = f.variables[varName]
    else:
      cropData = f.variables[varName][int(idx),:,:]       # still original data
    f = None 
    # PCRaster object
    return (cropData)


def getNetCDFTime(ncFile):    
    
    if ncFile in filecache.keys():
        f = filecache[ncFile]
        print "Cached: ", ncFile
    else:
        f = nc.Dataset(ncFile)
        filecache[ncFile] = f
        print "New: ", ncFile
    
    nctime = f.variables['time']  # A netCDF time variable object.
    
    return(len(nctime[:]))

def generate_Ensemble_Forcing_Name(self,orgFile,sampleNumber):
    splitName = str.split(orgFile, "_")
    splitName[4] = "r"+str(sampleNumber)+"i1p1"
    newFile = "_".join(splitName)
    return newFile

    
def matchCDF(data, orgDataCDF, refDataCDF, var="prec"):
    nx, ny, orgMax = orgDataCDF.shape
    refMax = refDataCDF.shape[2]
    
    if var == "prec":
        nonZero = orgDataCDF > 0.0
        nonZeroOrg = nonZero.argmax(2)-1
        
        nonZero = refDataCDF > 0.0
        nonZeroRef = nonZero.argmax(2)-1
        
    optDif = np.zeros((nx,ny))+9e9
    lowDif = np.zeros((nx,ny))
    highDif = np.zeros((nx,ny))
    optVal = np.zeros((nx,ny))+9e10
    out = np.zeros((nx,ny))
    
    for p in range(orgMax):
        absDif = np.abs(orgDataCDF[:,:,p] - data)
        improveVal = optDif > absDif
        optVal[improveVal] = p
        optDif[improveVal] = absDif[improveVal]
        lowDif[improveVal] = np.abs(orgDataCDF[:,:,np.max([p-1, 0])] - data)[improveVal]
        highDif[improveVal] = np.abs(orgDataCDF[:,:,np.min([p+1, orgMax-1])] - data)[improveVal]
    
    upInt = highDif+1e-05 < lowDif
    lowInt = highDif > lowDif+1e-05
    out = optVal
    out[upInt] = optVal[upInt] + optDif[upInt]/np.maximum(highDif[upInt] + optDif[upInt], 1e-10)
    out[lowInt] = optVal[lowInt] - optDif[lowInt]/np.maximum(lowDif[lowInt] + optDif[lowInt], 1e-10)
    out = out/(orgMax-1.)
    out[out < 0.0] = 0.0
    out[out > 100.0] = 100.0
    
    transData= np.zeros((nx,ny))
    out = out * (refMax-1.)
    for p in range(refMax):
        selVal = np.floor(out) == p
        maxVal = refDataCDF[:,:,np.min([p+1,refMax-1])][selVal]
        minVal = refDataCDF[:,:,np.max([p,0])][selVal]
        lowData = minVal + (out[selVal] - p) * (maxVal - minVal)
        highData = minVal + ((p+1) - out[selVal]) * (maxVal - minVal)
        transData[selVal] = (lowData + highData)/2
        if p == 0 and (var == "prec" or var == "prlr"):
            randomRainChance = np.maximum(nonZeroOrg - nonZeroRef,0.0)/np.maximum(nonZeroOrg, 1e-10)
            randomRainChance[randomRainChance >= 0.99999] = 2
            randomRain = (np.random.random((nx,ny)) - (1-randomRainChance)) / np.maximum(randomRainChance, 1e-10)
            randomRain[randomRain < 0] = 0.0
            randomRain[randomRain > 1.0] = 0.0
            rainPercentile = (nonZeroRef-0.001) + np.ceil((nonZeroOrg - nonZeroRef) * randomRain)
            out[selVal] = rainPercentile[selVal]
    
    return(transData)


def netcdf2PCRobjCloneMultiDim(ncFile,varName,dateInput,\
                       useDoy = None,
                       cloneMapFileName  = None,\
                       LatitudeLongitude = True,\
                       specificFillValue = None):
    # 
    # EHS (19 APR 2013): To convert netCDF (tss) file to PCR file.
    # --- with clone checking
    #     Only works if cells are 'square'.
    #     Only works if cellsizeClone <= cellsizeInput
    # Get netCDF file and variable name:
    #print ncFile
    if ncFile in filecache.keys():
        f = filecache[ncFile]
        print "Cached: ", ncFile
    else:
        f = nc.Dataset(ncFile)
        filecache[ncFile] = f
        print "New: ", ncFile
    
    varName = str(varName)
    
    if LatitudeLongitude == True:
        try:
            f.variables['lat'] = f.variables['latitude']
            f.variables['lon'] = f.variables['longitude']
        except:
            pass
    
    if varName == "evapotranspiration":        
        try:
            f.variables['evapotranspiration'] = f.variables['referencePotET']
        except:
            pass
    
    # date
    date = dateInput
    if useDoy == "Yes": 
        idx = dateInput - 1
    else:
        if isinstance(date, str) == True: date = \
                        datetime.datetime.strptime(str(date),'%Y-%m-%d')
        date = datetime.datetime(date.year,date.month,date.day)
        # time index (in the netCDF file)
        if useDoy == "month":
            idx = int(date.month) - 1
        else:
            nctime = f.variables['time']  # A netCDF time variable object.
            if useDoy == "yearly":\
                date = datetime.datetime(date.year,int(1),int(1))
            if useDoy == "monthly":\
                date = datetime.datetime(date.year,date.month,int(1))
            try:
                idx = nc.date2index(date, nctime, calendar = nctime.calendar, \
                                                  select='exact')
            except:                                  
                try:
                    idx = nc.date2index(date, nctime, calendar = nctime.calendar, \
                                                      select='before')
                    msg  = "\n"
                    msg += "WARNING related to the netcdf file: "+str(ncFile)+" ; variable: "+str(varName)+" !!!!!!"+"\n"
                    msg += "No "+str(dateInput)+" is available. The 'before' option is used while selecting netcdf time."
                    msg += "\n"
                except:
                    try:
                        idx = nc.date2index(date, nctime, calendar = nctime.calendar, \
                                                          select='after')
                        msg  = "\n"
                        msg += "WARNING related to the netcdf file: "+str(ncFile)+" ; variable: "+str(varName)+" !!!!!!"+"\n"
                        msg += "No "+str(dateInput)+" is available. The 'after' option is used while selecting netcdf time."
                        msg += "\n"
                    except:
                        idx = nc.date2index(date-datetime.timedelta(days=1), nctime, calendar = nctime.calendar, \
                                                          select='exact')
                        msg  = "\n"
                        msg += "WARNING related to the netcdf file: "+str(ncFile)+" ; variable: "+str(varName)+" !!!!!!"+"\n"
                        msg += "No "+str(dateInput)+" is available. The 'leapyear' option is used while selecting netcdf time."
                        msg += "\n"
                print msg
                                                  
    idx = int(idx)                                                  
    
    sameClone = True
    cropData = f.variables[varName][int(idx),:,:,:]       # still original data
    f = None 
    # PCRaster object
    return (cropData)

model = sys.argv[1]
ref = sys.argv[2]
year = sys.argv[3]
month = sys.argv[4]

zero = ""
if len(month) < 2:
  zero = "0"

varUnits = "degree C"

inputDir = model
outputDir = model+"_"+ref
files = glob.glob(inputDir+"/*"+year+zero+month+"01*")
files.sort()

for f in files:
  if f.split('.')[-1] == 'nc4':
    print f
    year = int(f.split('-')[-2][-8:-4])
    month = int(f.split('-')[-2][-4:-2])
    varNames = f.split('_')[0]
    if varNames == "tas":
      varUnits = "degree C"
      refVar = "tas"
    else:
      varUnits = "m/d"
      refVar = "prec"
    print varNames
    print varUnits
    createNetCDF(outputDir+"/"+f, refVar, varUnits, np.arange(89.5,-90,-1), np.arange(-179.5,180))
    fileLen = 365
    if (year/4. == np.floor(year/4.) and month <= 2) or \
      ((year+1)/4. == np.floor((year+1)/4.) and month >= 3):
      fileLen = 366
    if model != "FLOR":
      tempData = netcdf2PCRobjClone(model+"/"+f, varNames, datetime.datetime(year, month, 1), allData=True)
    else:
      tempData = netcdf2PCRobjClone(model+"/"+f, varNames, t+1, useDoy="Yes", allData=True)    
    for t in range(fileLen):
      dateInput = datetime.datetime(year, month, 1)+datetime.timedelta(days=t)
      print dateInput
      if dateInput.day == 1:
        refCDF = netcdf2PCRobjCloneMultiDim("resultsNetCDF/"+ref+"_"+refVar+"_pctl.nc4", refVar, dateInput, useDoy = 'month')
        orgCDF = netcdf2PCRobjCloneMultiDim("resultsNetCDF/"+model+"_"+varNames+"_pctl.nc4", varNames, dateInput, useDoy = 'month')
      matchData = matchCDF(tempData[t,:,:], orgCDF, refCDF, var=varNames)
      data2NetCDF(outputDir+"/"+f, refVar, matchData, dateInput, posCnt = t)

