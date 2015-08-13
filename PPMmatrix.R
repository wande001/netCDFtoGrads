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

models = c("CanCM3", "CanCM4", "FLOR")
var = c("prec","tas")
ref = c("CFS", "PGF")

continentNC = open.ncdf("../continents.nc")
continent = get.var.ncdf(continentNC, "con")
close.ncdf(continentNC)
continent[continent < 1] = NA
continent[continent > 2 & continent < 3] = NA
continent[continent > 3 & continent < 4] = NA
continent[continent > 4 & continent < 5] = NA
continent = mapFlip(continent)

outPPM = list()

varCount = 0
for(lag in c(0:3,6)){
  for(v in var){
    tel = 0
    varCount = varCount + 1
    outPPM[[varCount]] = array(NA, c(12,6, length(models)*length(ref)))
    for(m in models){
      for(r in ref){
        tel = tel + 1
        NC = open.ncdf(paste(m,r,v,"PPM.nc4", sep="_"))
        data = get.var.ncdf(NC, paste("Lead",lag, sep="_"))
        close.ncdf(NC)
        for(time in 1:12){
          temp = data[,,time]
          for(con in 1:6){
            outPPM[[varCount]][time,con,tel] = mean(temp[continent == con], na.rm=T)
          }
        }
      }
    }
    outPPM[[varCount]][outPPM[[varCount]] > 1] = NA
  }
}

A = makeMatrix(2,5)

pdf("../continentalPPM.pdf", width=10, height=4)

layout(A)
cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))(100)
colLen = length(cols)
par(mar=c(0,0,3,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,6), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.5,5.5,1), c("NA","EU","AF","SA","AS","OC"))
text(0.22, 3.0, "continent", srt=90, cex=1.5)

par(mar=c(2,0,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,6), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.8, seq(0.5,5.5,1), c("NA","EU","AF","SA","AS","OC"))
text(0.22, 3.0, "continent", srt=90, cex=1.5)


lagLabel = c(0,0,1,1,2,2,3,3,6,6)
for(i in seq(1,10,2)){
  par(mar=c(0,1,3,0))
  ensPPM = rowMeans(outPPM[[i]], na.rm=T, dims=2)
  image(x=seq(0.5,11.5,1), y=seq(0.5,5.5,1), ensPPM, xlab="", ylab="", col= cols, axes=FALSE, main=paste(lagLabel[i]," month lead", sep=""), zlim=c(0,1))
  abline(h=c(1:5), lty=2, col="grey")
  box()
}
for(i in seq(1,10,2)){
  par(mar=c(2,1.0,1,0))
  ensPPM = rowMeans(outPPM[[i+1]], na.rm=T, dims=2)
  image(x=seq(0.5,11.5,1), y=seq(0.5,5.5,1), ensPPM, xlab="", ylab="", col= cols, axes=FALSE, main="", zlim=c(0,1))
  axis(1, labels=c("J","F","M","A","M","J","J","A","S","O","N","D"), at=seq(0.5,11.5,1))
  abline(h=c(1:5), lty=2, col="grey")
  box()
}

par(mar=c(1,1,3,3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)

dev.off()
