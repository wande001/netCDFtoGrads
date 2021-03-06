require(ncdf)
require(fields)
require(akima)

models = c("CanCM3", "CanCM4", "FLOR")
var = c("prec", "tas")
ref = c("CFS", "PGF")

mapFlip <- function(map){
  temp = matrix(NA, dim(map)[1], dim(map)[2])
  half = dim(map)[1]/2
  end = dim(map)[1]
  temp[1:half,]=map[(half+1):end,]
  temp[(half+1):end,]=map[1:half,]
  return(temp)
}

makeMatrix <- function(rows, cols, size=5, legendSize = 2, labelSize = 1){
  A = matrix(rows*cols+3, rows*size, cols*size+legendSize+labelSize)
  A[1:size,1:labelSize] = 1
  A[(size+1):(2*size),1:labelSize] = 2
  for(i in c(1:(rows*cols))){
    row = floor((i-1)/cols)
    col = (i-1) - row * cols
    A[(row*size+1):(row*size+size),(col*size+1):(col*size+size)+labelSize] = i + 2
  }
  return(A)
}

continentNC = open.ncdf("../continents.nc")
continent = get.var.ncdf(continentNC, "con")
close.ncdf(continentNC)
continent[continent < 1] = NA
continent[continent > 2 & continent < 3] = NA
continent[continent > 3 & continent < 4] = NA
continent[continent > 4 & continent < 5] = NA
continent = mapFlip(continent)

outMatrix = list()

plotX = array()
plotY = array()
varTel = 0
for(lag in 0:11){
  for(time in 0:(12-lag)){
    varTel = varTel + 1
    plotX[varTel] = lag
    plotY[varTel] = time
  }
}

varCount = 0
for(v in var){
  varCount = varCount + 1
  outMatrix[[varCount]] = array(NA, c(90,7, length(models)*length(ref)))
  tel = 0
  for(m in models){
    for(r in ref){
      tel = tel + 1
      NC = open.ncdf(paste(m,r,v,"PPM_matrix_highLim.nc4", sep="_"))
      varTel = 0
      for(lag in 0:11){
        for(time in 0:(12-lag)){
          varTel = varTel + 1
          data = get.var.ncdf(NC, paste("PPM",lag,time, sep="_"))
          data[data > 1] = NA
          temp = rowMeans(data, dims=2, na.rm=T)
          for(con in 1:6){
            outMatrix[[varCount]][varTel,con,tel] = mean(temp[continent == con], na.rm=T)
          }
          outMatrix[[varCount]][varTel,7,tel] = mean(temp, na.rm=T)
        }
      }
      close.ncdf(NC)
    }
  }
}

pdf("../matrixPPM_highLim.pdf", width=10, height=4)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrix(2,7, labelSize=2)

layout(A)

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Precipitation temporal aggr.", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temperature temporal aggr.", srt=90)

xo = seq(0,11,0.1)
yo = seq(0,12,0.11)

title = c("North-America","Europe","Africa","South-America","Asia","Oceania")

par(mar=c(0,0,3,1))
v = 1
for(con in 1:6){
  plotZ = rowMeans(outMatrix[[v]][,con,], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, zlim=c(0,1), axes=FALSE, main=title[con])
  contour(fld, add=T, zlim=c(0,1))
}
plotZ = rowMeans(outMatrix[[v]][,7,], na.rm=T)
sel = which(plotZ <= 1)
fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
image(fld, col=cols, zlim=c(0,1), axes=FALSE, main="Global")
contour(fld, add=T, zlim=c(0,1))


par(mar=c(2,0,1,1))
v = 2
for(con in 1:6){
  plotZ = rowMeans(outMatrix[[v]][,con,], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}
plotZ = rowMeans(outMatrix[[v]][,7,], na.rm=T)
sel = which(plotZ <= 1)
fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
contour(fld, add=T, zlim=c(0,1))
axis(1, tick=FALSE, line=-1)
mtext("Lead time",1, cex=0.7, line=1)

par(mar=c(1,0.6,2,2.3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1, tick=FALSE, line=-0.7)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)

dev.off()

pdf("../matrixPPM_model_highLim.pdf", width=6, height=4)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrix(2,3, labelSize=1)

layout(A)

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Precipitation temporal aggr.", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temperature temporal aggr.", srt=90)

xo = seq(0,11,0.1)
yo = seq(0,12,0.11)

title = c("CanCM3", "","CanCM4","", "FLOR")

par(mar=c(0,0,3,1))
v = 1
for(mod in seq(1,5,2)){
  plotZ = rowMeans(outMatrix[[v]][,7,mod:(mod+1)], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE, main=title[mod])
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}


par(mar=c(2,0,1,1))
v = 2
for(mod in seq(1,5,2)){
  plotZ = rowMeans(outMatrix[[v]][,7,mod:(mod+1)], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}

par(mar=c(1,0.6,2,2.3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1, tick=FALSE, line=-0.7)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)

dev.off()

pdf("../matrixPPM_model_continent_highLim.pdf", width=10, height=4)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrix(2,7, labelSize=2)

layout(A)

for(mod in seq(1,5,2)){

  par(mar=c(0,0.2,3.0,0))
  plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
  text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
  text(0.22, 6.0, "Precipitation temporal aggr.", srt=90)

  par(mar=c(2,0.2,1,0))
  plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
  text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
  text(0.22, 6.0, "Temperature temporal aggr.", srt=90)

  xo = seq(0,11,0.1)
  yo = seq(0,12,0.11)

  title = c("North-America","Europe","Africa","South-America","Asia","Oceania")

  par(mar=c(0,0,3,1))
  v = 1
  for(con in 1:6){
    plotZ = rowMeans(outMatrix[[v]][,con,mod:(mod+1)], na.rm=T)
    sel = which(plotZ <= 1)
    fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
    image(fld, col=cols, zlim=c(0,1), axes=FALSE, main=title[con])
    contour(fld, add=T, zlim=c(0,1))
  }
  plotZ = rowMeans(outMatrix[[v]][,7,mod:(mod+1)], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, zlim=c(0,1), axes=FALSE, main="Global")
  contour(fld, add=T, zlim=c(0,1))

  par(mar=c(2,0,1,1))
  v = 2
  for(con in 1:6){
    plotZ = rowMeans(outMatrix[[v]][,con,mod:(mod+1)], na.rm=T)
    sel = which(plotZ <= 1)
    fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
    image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
    contour(fld, add=T, zlim=c(0,1))
    axis(1, tick=FALSE,line=-1)
    mtext("Lead time",1, cex=0.7, line=1)
  }
  plotZ = rowMeans(outMatrix[[v]][,7,mod:(mod+1)], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE, line=-1)
  mtext("Lead time",1, cex=0.7, line=1)

  par(mar=c(1,0.6,2,2.3))
  plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
  axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1, tick=FALSE, line=-0.7)
  symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)
}
  
dev.off()

pdf("../matrixPPM_bestPerformance_highLims.pdf", width=10, height=4)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrix(2,7, labelSize=1)

layout(A)

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Precipitation temporal aggr.", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temperature temporal aggr.", srt=90)

xo = seq(0,11,1.0)
yo = seq(0,12,1.0)

title = c("North-America","Europe","Africa","South-America","Asia","Oceania", "Global")

for(con in 1:7){
  par(mar=c(0,0,3,1))
  v = 1
  temp = array(0, c(90,5))
  plotZ = array(NA, 90)
  for(mod in seq(1,5,2)){
    temp[,mod] = rowMeans(outMatrix[[v]][,con,mod:(mod+1)], na.rm=T)
  }
  for(r in 1:90){
    plotZ[r] = which.max(temp[r,])
  }
  sel = which(is.na(plotZ) == FALSE)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,5), axes=FALSE, main=title[con])
#  contour(fld, add=T, zlim=c(0,5))
}
for(con in 1:7){

  par(mar=c(2,0,1,1))
  v = 2
  temp = array(0, c(90,5))
  plotZ = array(NA, 90)
  for(mod in seq(1,5,2)){
    temp[,mod] = rowMeans(outMatrix[[v]][,con,mod:(mod+1)], na.rm=T)
  }
  for(r in 1:90){
    plotZ[r] = which.max(temp[r,])
  }
  sel = which(is.na(plotZ) == FALSE)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,5), axes=FALSE)
  #contour(fld, add=T, zlim=c(0,5))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)

}

par(mar=c(1,0.6,2,2.3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1, tick=FALSE, line=-0.7)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)

dev.off()


