require(ncdf)

model = "CanCM3"
forcing = "PGF"
varName = "tas"
lim = 0.05
Rlim = 0.05

NC = open.ncdf(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",1,"_lag_",0,".nc", sep=""))

Lon = get.var.ncdf(NC, "lon")
Lat = get.var.ncdf(NC, "lat")
T = get.var.ncdf(NC, "time")

close.ncdf(NC)

dimX <- dim.def.ncdf( "lon", "degrees_north", Lon)
dimY <- dim.def.ncdf( "lat", "degrees_east", Lat)
dimT <- dim.def.ncdf( "time", "Days since 1901-01-01", T, unlim=TRUE)

mv <- -9999

PPM = list()
for(i in 0:11){
  PPM[[i+1]] <- var.def.ncdf(paste("PPM",i,sep="_"), "-", list(dimX, dimY, dimT), mv,prec="double")
}

nc <- create.ncdf(paste(model,"_",forcing,"_",varName,"_PPM.nc",sep=""), PPM)

CCevents = array(0,c(360, 180, 12))
count = 0
for(lag in 0:11){
  for(temp in 0:(12-lag)){
    NC = open.ncdf(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc", sep=""))
    print(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc", sep=""))
    for(spat in 0:8){
      if(temp ==0){
        for(time in 1:24){
          R = get.var.ncdf(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          sign = get.var.ncdf(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          out = matrix(0, 360, 180)
          out[sign< lim & R > Rlim] = 1
          count = count + 1
          CCevents[,,ceiling(time/2)] = CCevents[,,ceiling(time/2)] + out
        }
      }
      else{
        for(time in 1:12){
          R = get.var.ncdf(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          sign = get.var.ncdf(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          out = matrix(0, 360, 180)
          out[sign< lim & R > Rlim] = 1
          count = count + 1
          CCevents[,,time] = CCevents[,,time] + out
        }
      }
    }
    close.ncdf(NC)
  }
  put.var.ncdf(nc, PPM[[lag+1]], CCevents/(count/12))
  print(count)
  CCevents = array(0,c(360, 180, 12))
  count = 0
}

close.ncdf(nc)


