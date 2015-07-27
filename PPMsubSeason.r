require(ncdf)
require(fields)

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

outPPM = list()

varCount = 0
for(v in var){
  tel = 0
  varCount = varCount + 1
  outPPM[[varCount]] = array(NA, c(12,24, length(models)*length(ref)))
  for(m in models){
    for(r in ref){
      tel = tel + 1
      NC = open.ncdf(paste(m,r,v,"PPM_lead0_only.nc4", sep="_"))
      for(lag in 0:11){
      data = get.var.ncdf(NC, paste("Lead",lag, sep="_"))
        for(time in 1:24){
          temp = data[,,time]
          temp[temp > 1] = NA
          if(time/2 == floor(time/2)){
            outPPM[[varCount]][time/2,(lag+1)*2,tel] = mean(temp, na.rm=T)
          }
          else{
            outPPM[[varCount]][ceiling(time/2),(lag*2+1),tel] = mean(temp, na.rm=T)
          }
        }
      }
      close.ncdf(NC)
      }
    }
  outPPM[[varCount]][outPPM[[varCount]] > 1] = NA
}


pdf("../subSeasonPPM.pdf", width=10, height=4)

A = makeMatrix(2,3)
layout(A)

lim = 0.05

cols = colorRampPalette(c("grey","yellow" ,"green", "blue"))((1-lim)*100)
cols[1:(lim*100)] = "white"
colLen = length(cols)
par(mar=c(0,0,3,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,12), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.85, seq(0.5,11.5,1), c(1:12))
text(0.4, 6.0, "Lead time (months)", srt=90, cex=1.5)

par(mar=c(2,0,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,12), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.85, seq(0.5,11.5,1), c(1:12))
text(0.4, 6.0, "Lead time (months)", srt=90, cex=1.5)


lagLabel = c("CanCM3","" ,"CanCM4","", "FLOR")
for(i in seq(1,6,2)){
  par(mar=c(0,1,3,0))
  ensPPM =rowMeans(outPPM[[1]][,,i:(i+1)], na.rm=T, dims=2)
  image(y=seq(0.5,23.5,1), x=seq(0.5,11.5,1), ensPPM, xlab="", ylab="", col= cols, axes=FALSE, main=lagLabel[i], zlim=c(0.0,1))
  abline(h=seq(2,22,2), lty=2, col="grey")
  box()
}
for(i in seq(1,6,2)){
  par(mar=c(2,1.0,1,0))
  ensPPM = rowMeans(outPPM[[2]][,,i:(i+1)], na.rm=T, dims=2)
  image(y=seq(0.5,23.5,1), x=seq(0.5,11.5,1), ensPPM, xlab="Forecast initialization", ylab="", col= cols, axes=FALSE, main="", zlim=c(0.0,1))
  axis(1, labels=c("J","F","M","A","M","J","J","A","S","O","N","D"), at=seq(0.5,11.5,1))
  abline(h=seq(2,22,2), lty=2, col="grey")
  box()
}

par(mar=c(1,1,3,3))
plot(1,1,type="n", xlim=c(0,1), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="PPM")
axis(4, seq(0,1.0,0.1),seq(0,1.0,0.1), las=1)
symbols(rep(0.5,colLen), seq(0,1,length=colLen), rectangles=matrix(rep(c(1,1/colLen),2*colLen),colLen,2, byrow=T), inches=F, add=T, fg=cols, bg=cols)
box()

dev.off()
