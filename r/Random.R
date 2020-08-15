if (!require("ClimMobTools"))
{
        install.packages("ClimMobTools",repos="http://cran.rstudio.com/")
}

library("ClimMobTools")

args <- commandArgs(trailingOnly = TRUE)
ni <- as.integer(args[1])
no <- as.integer(args[2])
nv <- as.integer(args[3])
eval(parse(text=args[4]))

tableInfo <- randomise(ncomp = ni,
          nobservers = no,
          nitems = nv,
          itemnames = inames)

write.table( tableInfo, file=args[5], sep = "\t", row.names = FALSE, col.names = FALSE)


#Rscript Random.R 3 15 4 inames='c("1","2","3","4")' "/home/bmadriz/Desktop/comb_2.txt"