require(ncdf)
require(fields)
require(akima)

models = c("CanCM3","CanCM4", "FLOR")
var = c("prec", "tas")
ref = c("PGF", "CFS")

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

makeMatrixRows <- function(rows, cols, size=5, legendSize = 2, labelSize = 1){
  A = matrix(rows*cols+5, rows*size, cols*size+legendSize+labelSize)
  A[1:size,1:labelSize] = 1
  A[(size+1):(2*size),1:labelSize] = 2
  A[(2*size+1):(3*size),1:labelSize] = 3
  A[(3*size+1):(4*size),1:labelSize] = 4
  for(i in c(1:(rows*cols))){
    row = floor((i-1)/cols)
    col = (i-1) - row * cols
    A[(row*size+1):(row*size+size),(col*size+1):(col*size+size)+labelSize] = i + 4
  }
  return(A)
}


continentNC = open.ncdf("../continents.nc")
continent = get.var.ncdf(continentNC, "con")
close.ncdf(continentNC)
continent[continent < 1] = NA
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
  outMatrix[[varCount]] = array(NA, c(102,7, length(models)*length(ref)))
  tel = 0
  for(m in models){
    for(r in ref){
      tel = tel + 1
      print(paste(m,r,v,"PPM_matrix.nc4", sep="_"))
      NC = open.ncdf(paste(m,r,v,"PPM_matrix.nc4", sep="_"))
      varTel = 0    
      for(lag in 0:11){
        print(lag)
        time = 0
        varTel = varTel + 1
        plotX[varTel] = lag
        plotY[varTel] = 0.5
        NC2 = open.ncdf(paste(m,r,v,"PPM_lead0_only.nc4", sep="_"))
        data = get.var.ncdf(NC2, paste("Lead",floor(lag), sep="_"))
        close.ncdf(NC2)
        temp = rowMeans(data[,180:1,seq(1,24,2)], dims=2)
        temp[is.na(continent)] = NA
        for(con in 1:6){
          outMatrix[[varCount]][varTel,con,tel] = mean(temp[continent == con], na.rm=T)
        }
        outMatrix[[varCount]][varTel,7,tel] = mean(temp, na.rm=T)
        varTel = varTel + 1
        plotX[varTel] = lag+0.5
        plotY[varTel] = 0.5
        temp = rowMeans(data[,180:1,seq(2,24,2)], dims=2)
        temp[is.na(continent)] = NA
        for(con in 1:6){
          outMatrix[[varCount]][varTel,con,tel] = mean(temp[continent == con], na.rm=T)
        }
        outMatrix[[varCount]][varTel,7,tel] = mean(temp, na.rm=T)
        for(time in 1:(12-lag)){
          varTel = varTel + 1
          plotX[varTel] = lag
          plotY[varTel] = time
          data = get.var.ncdf(NC, paste("PPM",lag,time, sep="_"))
          data[data > 1] = NA
          temp = rowMeans(data, dims=2, na.rm=T)
          temp[is.na(continent)] = NA
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

pdf("../matrixPPM.pdf", width=10, height=7)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrix(2,7, labelSize=2)

layout(A)

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Precipitation temp. aggr.", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temperature temp. aggr.", srt=90)

xo = c(1,2,5,10,25,30,60,90,180,360)/360 #seq(0,11,0.1)
yo = c(1,2,5,10,25,30,60,90,180,360)/360 #seq(0,12,0.11)

title = c("North-America","Europe","Africa","South-America","Asia","Oceania")

par(mar=c(0,0,3,1))
v = 1
for(con in 1:6){
  plotZ = rowMeans(outMatrix[[v]][,con,], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, zlim=c(0,1), axes=FALSE, main=title[con])
  contour(fld, add=T, zlim=c(0,1), nlevels = 20)
}
plotZ = rowMeans(outMatrix[[v]][,7,], na.rm=T)
sel = which(plotZ <= 1)
fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
image(fld, col=cols, zlim=c(0,1), axes=FALSE, main="Global")
contour(fld, add=T, zlim=c(0,1), nlevels = 20)

par(mar=c(2,0,1,1))
v=2
for(con in 1:6){
  plotZ = rowMeans(outMatrix[[v]][,con,], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(fld, add=T, zlim=c(0,1), nlevels = 20)
  if(v == 1){
    axis(1, tick=FALSE,line=-1)
    mtext("Lead time",1, cex=0.7, line=1)
  }
}
plotZ = rowMeans(outMatrix[[v]][,7,], na.rm=T)
sel = which(plotZ <= 1)
fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
contour(fld, add=T, zlim=c(0,1), nlevels = 20)
if(v == 1){
  axis(1, tick=FALSE, line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}


par(mar=c(1,0.6,2,2.3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1, tick=FALSE, line=-0.7)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)

dev.off()

pdf("../matrixPPM_model.pdf", width=7, height=4)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrix(2,3, labelSize=1)

layout(A)

xLabel = c(0,15,30,45,60,75,90,120,150,180,270,335)
yLabel = c(15,30,60,90,120,150,180,270,335,365)

xo = xLabel/30.5
yo = yLabel/30.5
yo[1] = 0.51

xPlot = c(1:(length(xLabel)))
yPlot = c(1:(length(yLabel)))

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=length(yo)), yLabel)
text(0.22, 6.0, "Precipitation temporal aggr.", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=length(yo)), yLabel)
text(0.22, 6.0, "Temperature temporal aggr.", srt=90)

title = c("CanCM3", "","CanCM4","", "FLOR")

par(mar=c(0,0,3,1))
v = 1
for(mod in seq(1,5,2)){
  plotZ = rowMeans(outMatrix[[v]][,7,mod:(mod+1)], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(x=xPlot, y=yPlot, fld$z, col=cols, ylab="", xlab="", zlim=c(0,1), axes=FALSE, main=title[mod])
  contour(x=xPlot, y=yPlot,fld$z, add=T, zlim=c(0,1),labcex = 0.5)
}


par(mar=c(2,0,1,1))
v = 2
for(mod in seq(1,5,2)){
  plotZ = rowMeans(outMatrix[[v]][,7,mod:(mod+1)], na.rm=T)
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(x=xPlot, y=yPlot, fld$z, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(x=xPlot, y=yPlot,fld$z, add=T, zlim=c(0,1),labcex = 0.5)
  axis(1, at=xPlot, label=xLabel ,tick=FALSE,line=-1)
  mtext("Lead time (days)",1, cex=0.7, line=1)
}

par(mar=c(1,0.6,2,2.3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1, tick=FALSE, line=-0.7)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)

dev.off()

pdf("../matrixPPM_model_continent.pdf", width=10, height=4)

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

pdf("../matrixPPM_bestPerformance.pdf", width=10, height=4)

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


pdf("../matrixPPM_model_sepRef.pdf", width=6, height=7.5)

colLen =100
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(colLen)
A = makeMatrixRows(4,3, labelSize=1)

layout(A)

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Prec. temporal aggr. CFS", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Prec. temporal aggr. PGF", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temp. temporal aggr. CFS", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temp. temporal aggr. PGF", srt=90)

xo = seq(0,11,0.1)
yo = seq(0,12,0.11)

title = c("CanCM3", "","CanCM4","", "FLOR")

par(mar=c(0,0,3,1))
v = 1
for(mod in seq(1,5,2)){
  plotZ = outMatrix[[v]][,7,mod]
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE, main=title[mod])
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}

par(mar=c(2,0,1,1))
for(mod in seq(1,5,2)){
  plotZ = outMatrix[[v]][,7,mod+1]
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}

v = 2
for(mod in seq(1,5,2)){
  plotZ = outMatrix[[v]][,7,mod]
  sel = which(plotZ <= 1)
  fld <- interp(x = plotX[sel], y = plotY[sel], z = plotZ[sel], xo=xo ,yo=yo)
  image(fld, col=cols, ylab="", xlab="Lead time", zlim=c(0,1), axes=FALSE)
  contour(fld, add=T, zlim=c(0,1))
  axis(1, tick=FALSE,line=-1)
  mtext("Lead time",1, cex=0.7, line=1)
}

for(mod in seq(1,5,2)){
  plotZ = outMatrix[[v]][,7,mod+1]
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
