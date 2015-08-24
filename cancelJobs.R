jobs = c(5114448:5114501)
master=""

jobDir="../jobs/"

for(i in jobs){
  master = paste(master,"scancel ", i,"\n",sep="")
}
write.table(master, paste(jobDir,"cancel.sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE)
