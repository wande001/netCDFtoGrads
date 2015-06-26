jobs = c(4730195:4730300)
master=""

jobDir="../jobs/"

for(i in jobs){
  master = paste(master,"scancel ", i,"\n",sep="")
}
write.table(master, paste(jobDir,"cancel.sh",sep=""), col.names=FALSE, row.names=FALSE, quote=FALSE)
