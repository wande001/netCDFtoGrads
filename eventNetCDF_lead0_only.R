require(ncdf4)

modelS = c("CCSM") #c("CanCM3","CanCM4","FLOR")
forcingS = c("CFS","PGF")
varNameS = c("tas")
lim = 0.05
Rlim = 0.0

for(model in modelS){
for(forcing in forcingS){
for(varName in varNameS){

NC = nc_open(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",0,"_lag_",0,".nc4", sep=""))

Lon = ncvar_get(NC, "lon")
Lat = ncvar_get(NC, "lat")
T = ncvar_get(NC, "time")

nc_close(NC)

dimX <- ncdim_def( "lon", "degrees_north", Lon)
dimY <- ncdim_def( "lat", "degrees_east", Lat)
dimT <- ncdim_def( "time", "Days since 1901-01-01", T, unlim=TRUE)

mv <- -9999

PPM = list()
for(i in 0:11){
  PPM[[i+1]] <- ncvar_def(paste("Lead",i,sep="_"), "-", list(dimX, dimY, dimT), mv,prec="double")
}
# for(i in 0:12){
#   PPM[[i+1]] <- var.def.ncdf(paste("Time",i,sep="_"), "-", list(dimX, dimY, dimT), mv,prec="double")
# }
for(i in 0:8){
   PPM[[i+13]] <- ncvar_def(paste("Space",i,sep="_"), "-", list(dimX, dimY, dimT), mv,prec="double")
}

nc <- nc_create(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_PPM_lead0_only.nc4",sep=""), PPM)

CCevents = array(0,c(360, 180, 24))
count = 0
for(lag in 0:11){
  for(temp in 0){
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
          CCevents[,,time] = CCevents[,,time] + out
        }
      }
#       else{
#         for(time in 1:12){
#           R = get.var.ncdf(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           sign = get.var.ncdf(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           out = matrix(0, 360, 180)
#           out[sign< lim & R > Rlim] = 1
#           count = count + 1
#           CCevents[,,time] = CCevents[,,time] + out
#         }
#       }
    }
    nc_close(NC)
  }
  ncvar_put(nc, PPM[[lag+1]], CCevents/(count/24))
  print(count)
  CCevents = array(0,c(360, 180, 24))
  count = 0
}
rm(CCevents)
rm(R)
rm(sign)
rm(out)
# 
# CCevents = array(0,c(360, 180, 12))
# count = 0
# for(temp in 0:12){
#   for(lag in 0:min(12-temp,11)){
#     NC = open.ncdf(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc", sep=""))
#     print(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc", sep=""))
#     for(spat in 0:8){
#       if(temp ==0){
#         for(time in 1:24){
#           R = get.var.ncdf(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           sign = get.var.ncdf(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           out = matrix(0, 360, 180)
#           out[sign< lim & R > Rlim] = 1
#           count = count + 1
#           CCevents[,,ceiling(time/2)] = CCevents[,,ceiling(time/2)] + out
#         }
#       }
#       else{
#         for(time in 1:12){
#           R = get.var.ncdf(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           sign = get.var.ncdf(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           out = matrix(0, 360, 180)
#           out[sign< lim & R > Rlim] = 1
#           count = count + 1
#           CCevents[,,time] = CCevents[,,time] + out
#         }
#       }
#     }
#     close.ncdf(NC)
#   }
#   put.var.ncdf(nc, PPM[[temp+13]], CCevents/(count/12))
#   print(count)
#   CCevents = array(0,c(360, 180, 12))
#   count = 0
# }
# 
# rm(CCevents)
# rm(R)
# rm(sign)
# rm(out)
# 
CCevents = array(0,c(360, 180, 24))
count = 0

for(spat in 0:8){
  for(lag in 0:11){
    for(temp in 0){
      NC = nc_open(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc4", sep=""))
      print(paste("../resultsNetCDF/",model,"_",forcing,"_",varName,"_tempScale_",temp,"_lag_",lag,".nc4", sep=""))
      if(temp ==0){
        for(time in 1:24){
          R = ncvar_get(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          sign = ncvar_get(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
          out = matrix(0, 360, 180)
          out[sign< lim & R > Rlim] = 1
          count = count + 1
          CCevents[,,time] = CCevents[,,time] + out
        }
      }
#       else{
#         for(time in 1:12){
#           R = get.var.ncdf(NC, paste("correlation_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           sign = get.var.ncdf(NC, paste("signif_",spat, sep=""), start=c(1,1,time), count=c(360,180,1))
#           out = matrix(0, 360, 180)
#           out[sign< lim & R > Rlim] = 1
#           count = count + 1
#           CCevents[,,time] = CCevents[,,time] + out
#         }
#       }
      nc_close(NC)
    }
  }
  ncvar_put(nc, PPM[[spat+13]], CCevents/(count/24))
  print(count)
  CCevents = array(0,c(360, 180, 24))
  count = 0
}

rm(CCevents)
rm(R)
rm(sign)
rm(out)

nc_close(nc)

}}}

