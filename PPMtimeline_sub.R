require(ncdf)
require(fields)

models = c("CanCM3", "CanCM4", "FLOR")
var = c("prec", "tas")
ref = c("CFS", "PGF")

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

continentNC = open.ncdf("../continents.nc")
continent = get.var.ncdf(continentNC, "con")
close.ncdf(continentNC)
continent[continent < 1] = NA
continent[continent > 2 & continent < 3] = NA
continent[continent > 3 & continent < 4] = NA
continent[continent > 4 & continent < 5] = NA

outLead = list()

varCount = 0
for(v in var){
  for(lag in c(0)){
    tel = 0
    varCount = varCount + 1
    outLead[[varCount]] = array(NA, c(24,6, length(models)*length(ref)))
    for(m in models){
      for(r in ref){
        tel = tel + 1
        NC = open.ncdf(paste(m,r,v,"PPM_lead0_only.nc", sep="_"))
        data = get.var.ncdf(NC, paste("Lead",lag, sep="_"))
        close.ncdf(NC)
        for(time in 1:24){
          temp = data[,,time]
          for(con in 1:6){
            outLead[[varCount]][time,con,tel] = mean(temp[continent == con], na.rm=T)
          }
        }
      }
    }
  }
}

A = matrix(NA, 7, )
A[1:3,1] = 1
A[4:6,1] = 2
A[7,] = 3

#pdf("../skillTimeLine_sub.pdf", width=12, height=8)
layout(A)
parLeft = c(1,4,2,1)
parRight = c(1,1,2,4)
cols = tim.colors(13)
titles = c("Precipitation", "Temperature")

for(v in 1:length(var)){
  if(v ==1){
    par(mar=parLeft)
  }
  else{
    par(mar=parRight)
  }
  plot(1,1,type="n", xlim=c(0,24), ylim=c(0,6), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main=paste(titles[v], "lead time"))
  if(v ==2){
    axis(1, labels=c("J","F","M","A","M","J","J","A","S","O","N","D"), at=seq(0.5,11.5,1))
  }
  axis(2, labels=c("NA","EU","AF","SA","AS","OC"), at=seq(0.5,5.5,1), las=1, hadj=1, tick=FALSE)
  axis(4, rep(seq(0,0.5,0.5),6), at=seq(0,5.5,0.5), las=2)
  box()
  for(i in 1:12){
    ensPPM = rowMeans(outLead[[i+(v-1)*12]], na.rm=T, dims=2)
    for(con in 1:6){
      lines(seq(0.5,11.5,1), (ensPPM[,con]+con-1), type="b", col=cols[i], pch=19)
    }
  }
  abline(h=seq(0,5.5,0.5), lty=2)
  abline(h=seq(0,5,1))
}

par(mar=c(0,0,0,0))
plot(1,1,type="n", xlim=c(0,27), ylim=c(0,1), xaxs="i", yaxs="i", axes=FALSE, ylab="", xlab="", main="")
for(i in 1:13){
  lines(((i-0.5)*2):(i*2), rep(0.5,2), col=cols[i], type="b", pch=19)
  text(((i-0.25)*2), 0.3, i-1, cex=1.5)
}
dev.off()