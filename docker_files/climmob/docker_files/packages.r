if (!require("ClimMobTools"))
{
  remotes::install_github("agrobioinfoservices/ClimMobTools",
                        upgrade = "never",
                        force = TRUE)
}
if (!require("sf"))
{
  install.packages("sf")
}
if (!require("ggrepel"))
{
  install.packages("ggrepel")
}