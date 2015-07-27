require(ncdf)
require(fields)

mapFlip <- function(map){
  temp = matrix(NA, dim(map)[1], dim(map)[2])
  half = dim(map)[1]/2
  end = dim(map)[1]
  temp[1:half,]=map[(half+1):end,]
  temp[(half+1):end,]=map[1:half,]
  return(temp)
}

makeMatrix <- function(rows, cols, size=5, legendSize = 2, labelSize = 1){
  A = matrix(rows*cols+2, rows*size, cols*size+legendSize+labelSize)
  A[,1:labelSize] = 1
  for(i in c(1:(rows*cols))){
    row = floor((i-1)/cols)
    col = (i-1) - row * cols
    A[(row*size+1):(row*size+size),(col*size+1):(col*size+size)+labelSize] = i + 1
  }
  return(A)
}

models = c("CanCM3", "CanCM4", "FLOR")
var = c("prec")
ref = c("CFS", "PGF")
lagTimes = c(0:3,6)

continentNC = open.ncdf("../continents.nc")
continent = get.var.ncdf(continentNC, "con")
close.ncdf(continentNC)
continent[continent < 1] = NA
landMask = mapFlip(continent)

outPPM = list()

varCount = 0
for(lag in lagTimes){
  for(v in var){
    ensMean = array(0, c(360,180))
    for(m in models){
      varCount = varCount + 1
      outPPM[[varCount]] = array(NA, c(360,180, length(ref)))
      tel = 0
      for(r in ref){
        tel = tel + 1
        NC = open.ncdf(paste(m,r,v,"PPM.nc4", sep="_"))
        data = get.var.ncdf(NC, paste("Lead",lag, sep="_"))
        close.ncdf(NC)
        temp = rowMeans(data[,,], dims=2)
        outPPM[[varCount]][,,tel] = temp #mapFlip(temp)
      }
      ensMean = ensMean + rowMeans(outPPM[[varCount]], na.rm=T, dims=2)
    }
    varCount = varCount + 1
    outPPM[[varCount]] = ensMean/length(models)
  }
}

A = makeMatrix(length(lagTimes),length(models)+1)

pdf(paste("../skillMaps_",var,".pdf", sep=""), width=10, height =7)
layout(A)
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(100)
colLen = length(cols)
par(mar=c(0,0,2,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.5, seq(0.925,0.075,length=length(lagTimes)), paste("Lead", lagTimes), srt=90, cex=1.5)

par(mar=c(0,0,2,0))

titles = c(models, "Average")

for(p in seq(1,(length(models)+1)*length(lagTimes),1)){
  if(p/(length(models)+1) != floor(p/(length(models)+1))){
    ensPPM = rowMeans(outPPM[[p]], na.rm=T, dims=2)
  }
  else{
    ensPPM = outPPM[[p]]
  }
  ensPPM[is.na(landMask)] = NA
  title = ""
  ylabel = ""
  if(p < 5){title = titles[p]}
  image(x=seq(-179.5,179.5,1), y=seq(-89.5,89.5,1), ensPPM, xlab="", ylab="", col= cols, axes=FALSE, main=title, zlim=c(0,1), ylim=c(-59,89))
  world(add= TRUE)
}

par(mar=c(1,2,3,3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM score")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)
dev.off()


