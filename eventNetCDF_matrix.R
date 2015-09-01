require(ncdf4)

modelS = c("CCSM")#c("CanCM3","CanCM4","FLOR")
forcingS = c("CFS","PGF")
varNameS = c("tas")
lim = 0.05
Rlim = 0.0

for(model in modelS){
for(forcing in forcingS){
for(varName in varNameS){

NC = nc_open(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",1,"_lag_",0,".nc4", sep=""))

Lon = ncvar_get(NC, "lon")
Lat = ncvar_get(NC, "lat")
T = ncvar_get(NC, "time")

nc_close(NC)

dimX <- ncdim_def( "lon", "degrees_north", Lon)
dimY <- ncdim_def( "lat", "degrees_east", Lat)
dimT <- ncdim_def( "time", "Days since 1901-01-01", T, unlim=TRUE)

mv <- -9999

PPM = list()
tel = 0
for(i in 0:11){
  for(t in 0:(12-i)){
    tel = tel + 1
    PPM[[tel]] <- ncvar_def(paste("PPM",i,t,sep="_"), "-", list(dimX, dimY, dimT), mv,prec="double")
  }
}

nc <- nc_create(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_PPM_matrix_highLim.nc4",sep=""), PPM)

CCevents = array(0,c(360, 180, 12))
count = 0
varTel = 0
for(lag in 0:11){
  for(temp in 0:(12-lag)){
    varTel = varTel + 1
    NC = nc_open(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc4", sep=""))
    print(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc4", sep=""))
    for(spat in 0:8){
      if(temp ==0){
        for(time in 1:24){
          R = ncvar_get(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          sign = ncvar_get(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          out = matrix(0, 360, 180)
          out[sign< lim & R > Rlim] = 1
          count = count + 1
          CCevents[,,ceiling(time/2)] = CCevents[,,ceiling(time/2)] + out
        }
      }
      else{
        for(time in 1:12){
          R = ncvar_get(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          sign = ncvar_get(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          out = matrix(0, 360, 180)
          out[sign< lim & R > Rlim] = 1
          count = count + 1
          CCevents[,,time] = CCevents[,,time] + out
        }
      }
    }
    nc_close(NC)
    ncvar_put(nc, PPM[[varTel]], CCevents/(count/12))
    print(count)
    CCevents = array(0,c(360, 180, 12))
    count = 0
  }
}
rm(CCevents)
rm(R)
rm(sign)
rm(out)
}}}

