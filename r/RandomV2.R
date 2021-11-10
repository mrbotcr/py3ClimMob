if (!require("ClimMobTools"))
{
        install_github("agrdatasci/ClimMobTools", build_vignettes = TRUE)
}

library("ClimMobTools")

args <- commandArgs(trailingOnly = TRUE)
no <- as.integer(args[1])
eval(parse(text=args[2]))
eval(parse(text=args[3]))

tableInfo <- randomise(npackages = no,
          itemnames = inames,
          availability = iavailability)

write.table( tableInfo, file=args[4], sep = "\t", row.names = FALSE, col.names = FALSE)

