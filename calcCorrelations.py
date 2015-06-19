from readNC import *
from plotMatrix import *
from scipy.stats.stats import spearmanr

def lagToDateStr(date, lag):
    startDate = datetime.datetime.strptime(date,'%Y-%m-%d')
    y = startDate.year
    m = startDate.month
    if m+lag > 12:
        zero = ""
        if len(str(m-11+lag)) < 2: zero = "0"
        zero2 = ""
        if len(str(startDate.day)) < 2: zero2 = "0"
        tempEndDate = datetime.datetime.strptime(str(str(y+1)+"-"+str(m-12+lag)+"-"+zero2+str(startDate.day)),'%Y-%m-%d')
        newDate = str(tempEndDate.year) +"-"+ zero + str(tempEndDate.month) + "-" + zero2+str(startDate.day)
    else:
        zero = ""
        if len(str(m+lag)) < 2: zero = "0"
        zero2 = ""
        if len(str(startDate.day)) < 2: zero2 = "0"
        tempEndDate = datetime.datetime.strptime(str(str(y)+"-"+str(m+lag)+"-"+zero2+str(startDate.day)),'%Y-%m-%d')
        newDate = str(tempEndDate.year) +"-"+ zero + str(tempEndDate.month) + "-" + zero2+str(startDate.day)
    return(newDate)


def lagToDateTime(date, lag):
    startDate = datetime.datetime.strptime(date,'%Y-%m-%d')
    y = startDate.year
    m = startDate.month
    if m+lag > 12:
        zero = ""
        if len(str(m-11+lag)) < 2: zero = "0"
        zero2 = ""
        if len(str(startDate.day)) < 2: zero2 = "0"        
        tempEndDate = datetime.datetime.strptime(str(str(y+1)+"-"+str(m-12+lag)+"-"+zero2+str(startDate.day)),'%Y-%m-%d')
    else:
        zero = ""
        if len(str(m+lag)) < 2: zero = "0"
        zero2 = ""
        if len(str(startDate.day)) < 2: zero2 = "0"
        tempEndDate = datetime.datetime.strptime(str(str(y)+"-"+str(m+lag)+"-"+zero2+str(startDate.day)),'%Y-%m-%d')
    return(tempEndDate)


def returnSeasonalForecast(dateInput, endDay, model, varname, lag, ensNr = 1, dirLoc=""):
    deltaDay = lagToDateTime(endDay, lag) - lagToDateTime(dateInput, lag)
    
    data = np.zeros((deltaDay.days+1,180,360))
    
    print data.shape
    
    start = datetime.datetime.strptime(str(dateInput),'%Y-%m-%d')
    end = datetime.datetime.strptime(str(endDay),'%Y-%m-%d')
    
    for y in range(start.year, end.year+1):
        for m in range(1, 13):
            tempStartDate = datetime.datetime.strptime(str(str(y)+"-"+str(m)+"-01"),'%Y-%m-%d')
            zero = ""
            if len(str(m)) < 2: zero = "0"
            startDate = str(tempStartDate.year)+"-"+zero+str(tempStartDate.month)+"-01"
            tempEnd = datetime.datetime.strptime(str(str(y+1)+"-"+str(m)+"-01"),'%Y-%m-%d') - datetime.timedelta (days = 1)
            if tempStartDate >= start and tempStartDate < (end - datetime.timedelta (days = 1)):
                zero = ""
                if len(str(m)) < 2: zero = "0"
                zero2 = ""
                if len(str(tempEnd.month)) < 2: zero2 = "0"
                tempEndDate = lagToDateTime(startDate, lag+1)-datetime.timedelta(days=1)
                zero = ""
                if len(str(tempEndDate.month)) < 2: zero = "0"
                endDate = str(tempEndDate.year)+"-"+zero+str(tempEndDate.month)+"-"+str(tempEndDate.day)
                tempData = np.zeros((ensNr, 180,360))
                for ens in range(ensNr):
                    ncFile = "prlr_day_"+model+"_"+str(y)+zero+str(m)+"_r1i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc4"
                    if model == "FLOR":
                        ncFile = dirLoc+"pr_day_GFDL-FLORB01_FLORB01-P1-ECDA-v3.1-zero"+str(m)+str(y)+"_r"+str(ens+1)+"i1p1_"+str(y)+zero+str(m)+"01-"+str(tempEnd.year)+zero2+str(tempEnd.month)+str(tempEnd.day)+".nc"
                        print ncFile
                        tempData[ens,:,:] = readNC(ncFile,varName, lagToDateStr(startDate, lag), endDay = endDate, model=model)
                data[range((lagToDateTime(startDate, lag) - lagToDateTime(dateInput, lag)).days,(tempEndDate - lagToDateTime(dateInput, lag)).days+1),:,:] = ensembleMean(tempData)
    return(data)

def aggregateTime(data, breaks, timeDimension = 0):
    outPut = np.zeros(np.append(len(breaks), data.shape[1:3]))
    prev = 0
    count = 0
    for b in breaks:
        outPut[count, :, :] = data[prev:b,:,:].sum(axis=timeDimension)
        count += 1
        prev = b
    return(outPut)

def ensembleMean(data, ensDimension = 0):
    outPut = data[:,:,:].mean(axis=ensDimension)
    return(outPut)

def aggregateSpace(data, extent = 0):
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
    return(outPut/extent**2)


dateInput = "1981-01-01"
endDay = "1981-01-31"
model = "FLOR"
varName = "pr"
lag = 0
dirLoc = "output1.NOAA-GFDL.FLORB-01.day.atmos/"

NMME = returnSeasonalForecast(dateInput, endDay, model, varName, lag, dirLoc = dirLoc, ensNr = 12) * 86400.* 1000.

ncFile = "prec.nc"
varName = "prec"

dataPGF = readNC(ncFile, varName, lagToDateStr(dateInput, lag), endDay=lagToDateStr(endDay, lag), model="PGF")

spaceNMME = aggregateSpace(NMME, extent=1)
spacePGF = aggregateSpace(dataPGF, extent=1)

corMap = np.zeros((180,360))
signMap = np.zeros((180,360))

for i in range(180):
  for j in range(360):
    out = spearmanr(spacePGF[:,i,j], spaceNMME[:,i,j])
    corMap[i,j] = out[0]
    signMap[i,j] = out[1]

#corMap[signMap > 0.05] = 0.0

plotMatrix(corMap)

createNetCDF("corMap.nc", "Cor", "Spearman", range(-90,90), range(0,360))
data2NetCDF("corMap.nc", "Cor", corMap[:,0:360], lagToDateTime(dateInput, lag))

plotLine(dataPGF[:,100,100], NMME[:,100,100])

