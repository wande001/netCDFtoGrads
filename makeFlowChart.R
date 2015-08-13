require(fields)

colRamp = colorRampPalette(rev(c("red","orange","blue")))

pdf("../flowChart.pdf", width=8, height=3.3, pointsize=11)
A = matrix(c(1,1,1,2,2),1,5)
layout(A)

par(mar=c(4,4,0,0))

#plot(1,1, xlim=c(0,11.95), ylim=c(12,0), xaxs="i", yaxs="i", type="n", axes=FALSE, xlab="", ylab="Lead time (months)")

#blocks = matrix(1, 12, 2)

#ncols = 12
#Cols = colRamp(ncols)

#symbols(6, 6, rectangles=matrix(c(12,14),1,2), bg="gray95", fg="gray95", inches=FALSE, add=T)

#for(lag in 0:11){
#  symbols(seq(0.5,11.5,1)+lag, rep(lag+0.5,12), rectangles=blocks, bg=Cols, fg=Cols, inches=FALSE, add=T)
#}

#axis(1, labels=c("J","F","M","A","M","J","J","A","S","O","N","D"), at=seq(0.5,11.5,1))
#axis(2, c(0.5:11.5), c(0:11), las=1)
#box()

plot(1,1, xlim=c(0,11.95), ylim=c(13,0), xaxs="i", yaxs="i", type="n", axes=FALSE, ylab="Temporal Scale", xlab="Lead time (months)")
axis(1, c(0:11), c(0:11), las=1)
time = c(24,12:1)
month = c(1,1:12)
blocks=list()
for(lag in 1:13){
  blocks[[lag]] = matrix(c((12/time[lag])-0.02,1), time[lag], 2, byrow=T)
}

ncols = 13
Cols = rev(colorRampPalette(c("red","orange","blue"))(ncols))

symbols(6, 6.5, rectangles=matrix(c(12,15),1,2), bg="gray95", fg="gray95", inches=FALSE, add=T)

labels = c("J","F","M","A","M","J","J","A","S","O","N","D")

for(lag in 1:13){
  div = (6/time[lag])
  symbols(seq(0+div,12-div,div*2), rep(lag-0.5,time[lag]), rectangles=blocks[[lag]], bg=Cols[lag], fg="white", inches=FALSE, add=T)
  if(lag >= 2){
    label = array()
    for(t in 1:time[lag]){
      label[t] = paste(labels[t:(t+month[lag]-1)], collapse="")
    }
    text(seq(0+div,12-div,div*2), lag-0.5, label, col="white")
  }
  if(lag == 1){
    text(seq(0+div,12-div,div*2), lag-0.5, c(15, 16, 15, "13", 15,16, 15,15,15,16,15,15,15,16,15,16,15,15,15,16,15,15,15,16), col="white", cex=0.7)
  }
}

axis(2, c(0.5:12.5), c(0:12), las=1)
box()


ncols = 9
Cols = rev(colRamp(ncols))
par(mar=c(2,2,2,2))

plot(1,1, xlim=c(-125,-70), ylim=c(0,55), xaxs="i", yaxs="i", type="n", axes=FALSE, xlab="", ylab="")
for(size in 9:1){
  symbols(-90,40, rectangles=matrix(size*2-1,1,2), bg=rev(Cols)[size], fg="white", add=T, inches=FALSE)
}
US(add=T)
world(add=T)
symbols(seq(-120,-102,length=9),rep(15,9), rectangles=matrix(2,9,2), bg=rev(Cols)[1:9], fg=rev(Cols)[1:9], add=T, inches=FALSE)
text(seq(-120,-102,length=9),rep(12,9), parse(text=paste(abs(seq(1, 9, 1)), "^o ", sep="")))
text(-111, 9, "Spatial Scale")

dev.off()

