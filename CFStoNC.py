from readNC import *

start = datetime.datetime(1979,1,1)
time = start

data = readGrads('/tigress/gcoccia/CFSR-LAND/1hr/0.5deg/temp/tmp2m.gdas.ctl', "tmp2m", str(1))
createNetCDF("tas_CFSV2.nc", "tas", "K", latitudes=data.latitudes, longitudes=data.longitudes)
for i in np.arange(1, 306817,24):
    print i
    try:
        data = readGrads('/tigress/gcoccia/CFSR-LAND/1hr/0.5deg/temp/tmp2m.gdas.ctl', "tmp2m", str(i)+" "+str(i+23))
        out = np.mean(data, axis=0)
        data = None
    except:
        print "fail"
    time += datetime.timedelta(days =1)
    data2NetCDF("tas_CFSV2.nc", "tas", out, time)
