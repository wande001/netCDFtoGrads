from readNC import *

data = readGrads('/home/earth1/justin/global/forcings/1.0deg/daily/prec_correct/prec_1948-1948.ctl', "data", str(1))
createNetCDF("prec.nc", "prec", "mm/d", latitudes=data.latitudes, longitudes=data.longitudes)
for y in range(1948, 2015):
  end = 366
  if np.floor(y/4.)==y/4.: end = 367
  for i in range(1,end):
    print str(y) + " " + str(i)
    try:
      data = readGrads('/home/earth1/justin/global/forcings/1.0deg/daily/prec_correct/prec_'+str(y)+'-'+str(y)+'.ctl', "data", str(i))
      data2NetCDF("prec.nc", "prec", data, data.time)
    except:
      print "fail"

