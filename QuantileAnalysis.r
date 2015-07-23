require(ncdf)
require(fields)
require(akima)

models = c("CanCM3", "CanCM4", "FLOR")
var = c("prec", "tas")
ref = c("CFS", "PGF")

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

outMatrix = list()

varCount = 0
for(v in var){
  varCount = varCount + 1
  outMatrix[[varCount]] = array(NA, c(13,13, length(models)*length(ref)))
  #for(time in 0:(12-lag)){
  for(time in 0:4){
    tel = 0
    for(m in models){
      for(r in ref){
          print(paste(v,time,m,r))
          tel = tel + 1
          NC = open.ncdf(paste(m,r,v,"tempScale",time,"lag_0_quant.nc4", sep="_"))
          data = get.var.ncdf(NC, "uncorrected")
          quantTel = 0
          total = length(data)
          x = seq(0,1,0.1)
          if(m == "FLOR"){
            x = seq(0,1,length=13)
          }
          for(con in x){
            quantTel = quantTel + 1
            outMatrix[[varCount]][time+1,quantTel,tel] = length(which(data > con-0.01 & data < con+0.01))/total
          }
          close.ncdf(NC)
      }
    }
  }
}

A = makeMatrix(2,3, labelSize=1)
cols = colorRampPalette(c("red","blue"))(13)
layout(A)

par(mar=c(0,0.2,3.0,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Precipitation temporal aggr.", srt=90)

par(mar=c(2,0.2,1,0))
plot(1,1,type="n", xlim=c(0,1), ylim=c(-0.15,12.2), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
text(0.75, seq(0.2,11.8, length=7), seq(0,12,2))
text(0.22, 6.0, "Temperature temporal aggr.", srt=90)

for(m in c(1,3)){
  x = c(0,seq(0,1,0.1))
  plot(1,1, xlim=c(0,1), ylim=c(0,1), type="n", axes=FALSE)
  for(time in 0:2){
    y = c(0,cumsum(rowMeans(outMatrix[[1]][time+1,1:11,m:(m+1)], na.rm=T)))
    lines(x, y, col=cols[time+1])
  }
}
plot(1,1, xlim=c(0,1), ylim=c(0,1), type="n", axes=FALSE)
x = c(0,seq(0,1,length=13))
for(time in 0:2){
  y = c(0,cumsum(rowMeans(outMatrix[[1]][time+1,,5:6], na.rm=T)))
  lines(x, y, col=cols[time+1])
}

for(m in c(1,3)){
  x = c(0,seq(0,1,0.1))
  plot(1,1, xlim=c(0,1), ylim=c(0,1), type="n", axes=FALSE)
  for(time in 0:2){
    y = c(0,cumsum(rowMeans(outMatrix[[2]][time+1,,m:(m+1)], na.rm=T)))
    lines(x, y, col=cols[time+1])
  }
}
plot(1,1, xlim=c(0,1), ylim=c(0,1), type="n", axes=FALSE)
x = c(0,seq(0,1,length=13))
for(time in 0:2){
  y = c(0,cumsum(rowMeans(outMatrix[[2]][time+1,,5:6], na.rm=T)))
  lines(x, y, col=cols[time+1])
}
