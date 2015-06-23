from readNC import *

start = datetime.datetime(1979,1,1)
time = start

data = readGrads('/tigress/gcoccia/CFSR-LAND/1hr/0.5deg/prec/prate.gdas.ctl', "data", str(1))
createNetCDF("prec_CFS.nc", "prec", "mm/d", latitudes=data.latitudes, longitudes=data.longitudes)
data = np.zeros((360,720))
for i in range(1, 306817):
    print i
    try:
        data += readGrads('/tigress/gcoccia/CFSR-LAND/1hr/0.5deg/prec/prate.gdas.ctl', "pratesfc", str(i))
    except:
        print "fail"
    if i/24. == i/24:
        print "write"
        time += datetime.timedelta(days =1)
        data2NetCDF("prec_CFS.nc", "prec", data, time)
        data = np.zeros((360,720))
