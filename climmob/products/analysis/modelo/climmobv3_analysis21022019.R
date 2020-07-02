## ---------------------------------------------------
## ---------------------------------------------------
## Analyse the performance of crop varieties from 
## crowdsourcing trials using Plackett-Luce model
## ---------------------------------------------------
## ---------------------------------------------------
## Bioversity International - Costa Rica Office
## https://github.com/BioversityCostaRica/
## Updated 21Feb2019
## ---------------------------------------------------
## ---------------------------------------------------
#system("R-script, climmobv3_analysis.R info.json data.json r.json /output/ TRUE TRUE")
#args <- c("info.json", "data.json", "r.json", "/output/result/here", TRUE , TRUE)

# get the arguments
args <- commandArgs(trailingOnly = TRUE)
mydataname     <- args[1] #a json file with trial data
infoname       <- args[2] #a json file with parameters
outputname     <- args[3] #a json file with the results
pathname       <- args[4] #the path where results will be written
overallVSlocal <- as.logical(args[5]) #logical() TRUE FALSE
infosheets     <- as.logical(args[6]) #logical() TRUE FALSE


## Packages
library("tidyverse")
library("ggplot2")
library("plotly")
library("jsonlite")
library("partykit")
library("qvcalc")
library("psychotools")
library("PlackettLuce")

## ---------------------------------------------------
## ---------------------------------------------------
## Read data 
mydata <- jsonlite::read_json(mydataname)

## Read data with selected traits and explanatory variables to be analysed
info <- jsonlite::read_json(infoname)

## ---------------------------------------------------
## ---------------------------------------------------
## Extra functions 
# Plot nodes using qvcalc and ggplot2
plot_nodes <- function(object, labels = NULL, ...){
  
  # extract ids from terminal nodes
  node_id <- partykit::nodeids(object, terminal = TRUE)
  
  dots <- list(...)
  
  # check font size for axis X and Y, and plot title
  if ("font.size" %in% names(dots)) {
    font.size <- dots[["font.size"]]
    s.title <- font.size[1]
    s.axis <- font.size[2]
  } else {
    s.title <- 13
    s.axis <- 12
  }
  
  
  # get node information
  nodes <- list()
  for (i in seq_along(node_id)) {
    nodes[[i]] <- object[[ node_id[i] ]]$node$info$object
  }
  
  # get item names
  items <- names(object[[node_id[1]]]$node$info$coefficients)
  
  # get number of observers in each node
  nobs <- list()
  for (i in seq_along(node_id)) {
    nobs[[i]] <- as.integer(object[[ node_id[i] ]]$node$info$nobs) 
  }
  
  # get item parameters from PlackettLuce
  coeffs <- lapply(nodes, psychotools::itempar)
  
  # get estimates from item parameters using qvcalc
  coeffs <- lapply(coeffs, qvcalc::qvcalc)
  
  # extract dataframes with estimates
  coeffs <- lapply(coeffs, function(X){
    df <- X[]$qvframe }
  )
  
  # Add limits in error bars and item names
  coeffs <- lapply(coeffs, function(X){
    X <- within(X, {
      bmin <- X$estimate-(X$quasiSE)
      bmax <- X$estimate+(X$quasiSE)
      items <- items
    })
    
    X$bmax <- ifelse(X$bmax > 1, 0.991, X$bmax)
    
    X$bmin <- ifelse(X$bmin < 0, 0.001, X$bmin)
    return(X)
  })
  
  # Add node information and number of observations
  for (i in seq_along(node_id)) {
    coeffs[[i]] <- within(coeffs[[i]], {
      nobs <- nobs[[i]]
      node <- node_id[i]}
    )
  }
  
  # Get max and min values for the x axis in the plot
  xmax <- round(max(do.call(rbind, coeffs)$bmax, na.rm = TRUE) + 0.01, digits = 4)
  xmin <- round(min(do.call(rbind, coeffs)$bmin, na.rm = TRUE), digits = 4)
  
  # Check labels for axis Y
  if (is.null(labels)) {
    labels <- coeffs[[1]]$items
  }
  
  # Check dimensions of labels
  if (length(labels) != length(coeffs[[1]]$items)) {
    stop("wrong dimensions in labels \n")
  }
  
  
  # Plot winning probabilities
  plots <- lapply(coeffs, function(X){
    
    p <- ggplot(X, aes(x = X$estimate, y = labels)) +
      geom_vline(xintercept = 1/length(X$items), 
                 colour = "#E5E7E9", size = 0.8) +
      geom_point(pch = 21, size = 2, 
                 fill = "black",colour = "black") +
      geom_errorbarh(aes(xmin = X$bmin,
                         xmax = X$bmax),
                     colour="black", height = 0.2) +
      scale_x_continuous(limits = c(0, xmax)) +
      theme_bw() +
      labs(x = NULL, y = NULL ,
           title = paste0("Node ", X$node[1], " (n= ", X$nobs[1], ")")) +
      theme(plot.title = element_text(size = s.title),
            axis.text.x = element_text(size = s.axis, angle = 0,
                                       hjust = 0.5, vjust = 1, face = "plain",
                                       colour = "black"),
            axis.text.y = element_text(size = s.axis, angle = 0,
                                       hjust = 1, vjust = 0.5, face = "plain",
                                       colour = "black"),
            plot.background = element_blank(),
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            panel.border = element_rect(colour = "black", size = 1),
            axis.ticks = element_line(colour = "black", size = 0.5),
            axis.ticks.length=unit(0.3, "cm"))
    
    p
    
  })
  
  names(plots) <- paste0("node",node_id)
  
  return(plots)
}

#  Convert a data.frame into a object of class rankings
fromtricot <- function(items, r, 
                       local.rankings = NULL){
  
  n <- nrow(items)
  
  # fix names in r and items
  # first column must always be the best and the 
  # second the worst
  names(r) <- c("best", "worst")
  names(items) <- paste0("Item",1:3)
  
  # rankings can be LETTERS (A, B, C) or integer (1, 2, 3)
  # convert it to factor and then to integer in case values are LETTERS
  # keep as integer to allow us to impute the middle-ranked item
  # (a strict ranking is assumed here, so the sum of each row should always be 6)
  r <- within(r,{ 
    best = as.integer(as.factor(best))
    worst = as.integer(as.factor(worst))
    middle = 6 - best - worst
  })
  
  # if there is any NA in items and observations with only two items
  # add a pseudo-item which will be removed later
  if (sum(is.na(items)) > 0)  {
    items[is.na(items)] <- "pseudoitem"
  }
  
  # combine items with rankings
  r <- cbind(items, r)
  
  # convert items in a matrix
  items <- as.matrix(items)
  
  # then convert the itemsIDs to the item names
  r <- within(r,{
    best = items[cbind(seq_len(n), best)]
    worst = items[cbind(seq_len(n), worst)]
    middle = items[cbind(seq_len(n), middle)]
  })
  
  # get vector with item names
  itemnames <- sort(unique(unlist(data.frame(items, stringsAsFactors = FALSE ))))
  
  # convert the orderings of the items given to each observer to 
  # sub-rankings of the full set of varieties:
  R <- PlackettLuce::as.rankings(r[c("best","middle","worst")], 
                                 input = "ordering", 
                                 labels = itemnames)
  
  # keep this for infosheets 
  positions <- r[c("best","middle","worst")]
  names(positions) <- paste0("Position",1:3)
  
  # if pseudo-item were added, it is removed
  if ("pseudoitem" %in% itemnames) {
    R <- R[,-match("pseudoitem", itemnames)]
  }
  
  # if comparison with local is required then use it
  if (!is.null(local.rankings)) {
    
    # get local.rankings in a separeted object
    lr <- local.rankings
    names(lr) <- paste0("localVSitem", 1:3)
    
    #add lr to r
    r <- cbind(r, lr)
    
    # treat the paired comparisons as additional rankings.
    # first we can convert the orderings of the trial varieties to 
    # sub-rankings of the full set of items including the local 
    # as an additional item, so that we can add the paired comparisons 
    # shortly the comparisons with the local item are stored 
    # in another set of columns
    
    # add local to itemnames
    itemnames <- c("Local", itemnames)
    
    paired <- list()
    
    for (id in 1:3) {
      ordering <- matrix("Local", nrow = n, ncol = 2)
      worse <- r[[paste0("localVSitem", id)]] == 2
      ## name of winner
      ordering[!worse, 1] <- r[[paste0("Item", id)]][!worse]
      ## name of loser
      ordering[worse, 2] <- r[[paste0("Item", id)]][worse]
      paired[[id]] <- ordering
    }
    # again we convert these orderings to sub-rankings of the full set of items
    # and combine them with the rankings of order three:
    paired <- lapply(paired, function(x) {
      x <- PlackettLuce::as.rankings(x, input = "ordering", labels = itemnames)
    })
    
    R <- rbind(R, paired[[1]], paired[[2]], paired[[3]])
    
  }
  
  if (!is.null(local.rankings)) {
    G <- PlackettLuce::grouped_rankings(R, index = rep(seq_len(n), 4))
  }else{
    G <- PlackettLuce::grouped_rankings(R, index = seq_len(n))
  }
  
  return(list(R, G, positions))
  
}

# rankings into a PlackettLuce ranking object
fromrank <- function(id, items, r){
  
  n <- nrow(items)
  
  # fix names in r data 
  names(r) <- paste0("PosItem",1:ncol(r))
  # get the number of possible rankings
  nrank <- ncol(r)
  
  # if there is any NA in items
  # add a pseudo-item which will be removed later
  if (sum(is.na(items)) > 0)  {
    for (i in seq_len(nrank)) {
      items[is.na(items[i]), i] <- paste0("pseudoitem",i)
    }
  }
  
  # add 0 if there is any missing ranking in r
  if (sum(is.na(r)) > 0)  {
    r[is.na(r)] <- 0
  }
  
  # combine items with rankings
  r <- cbind(id, items, r)
  
  # convert data into long format
  r <- cbind(reshape2::melt(r[c(paste0("Item", 1:nrank), "id")], 
                            id.vars = "id"),
             reshape2::melt(r[c(paste0("PosItem", 1:nrank), "id")], 
                            id.vars = "id"))
  
  # select only id, items and rankings
  r <- r[c(1,3,6)]
  names(r) <- c("id","item","rank")
  
  # arrange elements by its id
  r <- dplyr::arrange(r, as.integer(id))
  
  # if pseudo-item were added, it is removed now
  rmitem <- !r[["item"]] %in% paste0("pseudoitem", 1:nrank)
  r <- r[rmitem,]
  
  # if values in rankings are numeric 
  # then we group it by ids and convert it 
  # into integer ranks
  # the highest value is the best item
  # negative values are allowed 
  # they are added in the last place
  if (any(is_decimal(r[["rank"]]))) {
    r <- num2rank(r)
  }
  
  # reshape data into wide format
  r <- tidyr::spread(r, item, rank)
  
  # replace possible NA's with zeros (0) as required for PlackettLuce
  r[is.na(r)] <- 0
  
  # arrange observations by ids
  r <- dplyr::arrange(r, as.integer(id))
  
  # drop id
  r <- r[ ,-match("id", names(r))]
  
  # dataframe into matrix
  R <- as.matrix(r)
  
  # make a PlackettLuce ranking
  R <- PlackettLuce::as.rankings(R)
  
  R <- PlackettLuce::grouped_rankings(R, index = seq_len(n))
  
  return(R)
  
} 


## ---------------------------------------------------
## ---------------------------------------------------
## Get variables names and key information on this dataset

## Number of comparisons in each trial (often 3) 
ncomp <- mydata$project$project_numcom

if(ncomp > 3){
  stop("\nAnalysis with more than 3 comparisons not supported yet")
}

## Convert vector list of important fields into a tibble
impfields <- mydata$importantfields

impfields <- lapply(impfields, function(X){
  names(X) <- paste0("V", 1:length(X))
  X
})

impfields <- bind_rows(impfields)

impfields <- mutate(impfields, V1 = tolower(V1))

## ---------------------------------------------------
## ---------------------------------------------------
## Get a tibble with the names of explanatory variables 
## to be considered in the analysis
varNames <- info[[2]]

if (!is_empty(varNames)) {
  varNames <- lapply(varNames, function(X){
    names(X) <- paste0("V",1:length(X)); X
    })
  varNames <- do.call(rbind, varNames)
}

if (is_empty(varNames)) {
  cat("\nWarning: no explanatory variables selected. Fitting models with only the intercept\n")
}

## ---------------------------------------------------
## ---------------------------------------------------
## Get a tibble describing selected characteristics (traits)
## to be analysed
charNames <- info[[1]]
charNames <- lapply(charNames, unlist)

charNames <- lapply(charNames, function(X){
  names(X) <- paste0("V",1:length(X)) ; X
  })

charNames <- do.call(rbind, charNames)

charNames <- as_tibble(charNames)

## Look for the alias for package id 
id <- t(impfields[,2]) %in% "PackageID"
id <- as.character(impfields[id, 2])

## ---------------------------------------------------
## ---------------------------------------------------
## Get the names of technologies and packages ids
pack <- mydata$packages

# get name of technology
techname <- pack[[1]]$comps[[1]]$technologies[[1]]$tech_name

# unlist pack information and convert into a dataframe 
pack <- lapply( pack , unlist)
pack <- do.call(rbind, pack)
pack <- as.data.frame(pack, stringsAsFactors = FALSE)

# keep only tecnologies and package id
comps <- pack[, (which(names(pack) %in% "comps.comb_order") + 2)]

pack <- cbind(pack$package_id, comps)

pack <- as_tibble(pack)

pack[1:ncol(pack)] <- lapply(pack[1:ncol(pack)], as.character)

# rename colunms
names(pack) <- c(id,paste0("tech_",LETTERS[1:ncomp]))

## Take the vectors with of technologies among packages (item names)
items <- pack[,2:ncol(pack)]

# get vector with item names
itemNames <- as.character(sort(unique(unlist(items))))

## ---------------------------------------------------
## ---------------------------------------------------
## Get the trial data and explanatory variables
df <- mydata$data

if(is_empty(df)){
  stop("\nNo data assessment data found. Please check your assessments\n")
}

names_df <- tolower(names(df[[1]]))

## Convert the list into a dataframe
## first, convert each entry into characters 
## to make sure that NULL values will be retained
## and maintain the same length when bind rows
df <- lapply( df , as.character)
df <- lapply( df , unlist)
df <- do.call(rbind, df)
df <- as.data.frame(df, stringsAsFactors = FALSE)

## Get the original colnames for this dataset
names(df) <- names_df

## Convert NULL values into NA
df[1:ncol(df)] <- lapply(df[1:ncol(df)], function(X){
  ifelse(X == "NULL", NA, X)
})

df <- as_tibble(df)

## ---------------------------------------------------
## ---------------------------------------------------
## Get explanatory variables in a different dataframe
## and check for labels in codes
if (!is_empty(varNames)) {
  expvar <- df[ ,as.character(tolower(t(varNames[,2]))) ]
}

# if explanatory variables are missing
# create a pseudo variable 
if (is_empty(varNames)) {
  expvar <- tibble(P1 = rep(1, nrow(df)))
}

# check if geografic location is required
geoTRUE <- grepl("farmgoelocation|ubicacion", names(expvar))

## If geolocation info is required, then split the vector into its 
## respectives colunms (lon, lat)
if(any(geoTRUE)){
  geo <- separate(expvar[geoTRUE], names(expvar[geoTRUE]),
                  c("lat","lon"), sep = " ", remove = TRUE,
                  extra = "drop") 
  #convert coordinates into numeric 
  geo[c("lat","lon")] <- lapply(geo[c("lat","lon")], as.numeric)
  #add rotated axis
  geo <-   within(geo, 
                  {xy <- lon + lat
                  yx <- lon - lat
                  })
  
  #combine with others variables
  expvar <- bind_cols(expvar[!geoTRUE], geo)
  
}

## ---------------------------------------------------
## ---------------------------------------------------
## Get the trial data from important fields and charNames
# combine name from different sources
# make a matrix, the firts column is the current names of variables in df
# the second column is the alias (names without codes from ODK)
trialdata <- cbind(names = tolower(c(impfields[[1]],charNames[[2]], charNames[[3]])),
                   aliases = c(impfields[[2]],
                               paste0(charNames[[1]],
                                      rep(c("Pos","Neg"), each = nrow(charNames)))))
# remove duplicates in trialdata 
# I DON'T KNOW WHY IT HAPPENS
trialdata <- trialdata[!duplicated(trialdata[, 1]),]

# keep only colunms in trialdata
df <- df[trialdata[,1]]

# change names using aliases
names(df) <- trialdata[,2]

# Get the names of characteristics to be avaluated 
char <- names(df)[3:ncol(df)]
char <- gsub("Pos|Neg|Perf|[1-9]|Char|Characteristic| ", "", char)
char <- sort(unique(char))
# Put Overall as the last characteristic to be evaluated
char <- c(char[!char %in% "Overall"],  char[char %in% "Overall"])

# Remove case "Char" in df names
names(df) <- gsub("|Char|Characteristic| ","",names(df))

# merge trial data with packages information
df <- inner_join(pack, df, by = id, all.x = TRUE)

## ---------------------------------------------------
## ---------------------------------------------------
# Run Plackett-Luce model over characteristics
# List to keep all outputs
results <- vector(mode="list", length = 3+length(char))
names(results) <- c("Items","Characteristics",char,"Infosheets")
Items <- as.data.frame(cbind(techName = techname, aliasName = itemNames))
results[["Items"]] <- apply(Items, 1, as.list)
results[["Characteristics"]] <- as.list(char)
R_all <- array("NA", dim=c(nrow(df),ncomp, length(char)),
               dimnames = list(1:nrow(df), 1:ncomp , seq_along(char)))

# check if output dir exists,
# if not, create the dir
if(!file.exists(pathname)){
  
  x <- unlist(strsplit(pathname, "[/]"))
  
  x <- x[!x %in% ""]
  
  pathname <- paste(x, collapse = "/")
  
  dir.create(pathname, showWarnings = FALSE, recursive = TRUE)
  
}


for(i in seq_along(char)){
  
  char_i <- char[i]
  cat("\n\nAnalysing the performance in:", char_i , "\n")
  
  #Get the rankings for the characteristic to be analysed in this run
  df_i <- df[,c(names(pack), paste0(char_i, c("Pos","Neg")))]
  
  # Convert values of observer's evaluation into integer
  use <- grepl(char_i, names(df_i))
  df_i[use] <- lapply(df_i[use], as.integer)
  
  # convert this dataframe into a grouped_rankings object
  if (ncomp == 3) {
    
    myitems <- df_i[paste0("tech_", LETTERS[1:3])]
    myrank <- df_i[use]
    
    # check if the information is complete
    keep <- !is.na(rowSums(myrank))
    
    # Keep the check when overall vs local is TRUE
    if(char_i == "Overall" & overallVSlocal){
      
      local_rank <- df[paste0("OverallPerf", 1:3)]
      
      local_rank[1:3] <- lapply(local_rank[1:3], as.integer)
      
      keep2 <- !is.na(rowSums(local_rank))
      
      keep <- keep & keep2
      
      local_rank <- local_rank[keep,]
      
      # numbers mean Best == 1 and Worse == 2
      
    }else{
      local_rank <- NULL
    }
    
    # remove NAs 
    myrank <- myrank[keep,]
    
    myitems <- myitems[keep,]
    
    myrank <- fromtricot(items = myitems,
                         r = myrank,
                         local.rankings = local_rank)
    
    # the rankings
    R <- myrank[[1]]
    
    # the grouped rankings 
    G <- myrank[[2]]
    
    # add to the array for infosheets
    R_all[keep, , i] <- as.matrix(myrank[[3]])
    
  }
  
  #Now check missing data for explanatory variables
  #First get a logic list of non NA values
  x <- lapply(expvar[1:ncol(expvar)], function(X) !is.na(X)) 
  #Then keep those values where the sum is equal to ncomp
  x <- matrix(unlist(x), ncol = ncol(expvar), nrow = nrow(expvar))
  #Refresh keep
  keep <- rowSums(x) == ncol(expvar) & keep
  
  #apply keep to expvar
  expvar_i <- expvar[keep, ]
  if (length(varNames) == 0) {
    names(expvar_i) <- "P1"
  }
  if (length(varNames) > 0) {
    names(expvar_i) <- as.vector(tolower(t(varNames[,2])))
  }
  
  #Get the number of valid values
  nR <- sum(keep)
  
  if (nrow(df)-nR > 0) {
    cat("\n",nrow(df)-nR, "observations removed due to incosistent rankings or missing values \n")
    cat("Using", nR, "of", nrow(df), "observations \n" )
  }
  
  #Fit the model without explanatory variables 
  mod <- PlackettLuce(R)
  #Get table with coefficients and p values 
  mod_coeff <- qvcalc(mod, ref = NULL)$qvframe
  #Add row names (item names) to column
  mod_coeff <- rownames_to_column(mod_coeff, var = "Item")
  #Transform this dataframe into a list
  mod_coeff <- apply(mod_coeff, 1,  as.list)
  
  #Bind explanatory variables and grouped rankings
  G <- cbind(G, expvar_i)
  
  #Fit Plackett-Luce tree
  tree <- pltree(G ~ . , data = G, 
                 alpha = 0.05)
  
  # Make a plot for the tree
  # first using modelparty from partykit
  # write it and keep the path 
  svg(filename = paste0(pathname, "/", char_i,"_tree.svg"),
      width=6.5,
      height=6.5,
      pointsize=12)
  par(mgp=c(2.2,0.45,0), tcl=-0.4, mar=c(0,0,0,0))
  partykit::plot.modelparty(tree) 
  dev.off()
  
  treepath <- paste0(pathname, "/", char_i,"_tree.svg")
  
  # then using quasi-variance from qvcalc 
  # this will genenerate one plot per node
  # write it and keep the path
  # get plots
  plots <- plot_nodes(tree)
  #define names
  nodepaths <- paste0(pathname, "/", char_i,"_tree", names(plots) ,".svg")
  #put names in a list
  nodepaths <- as.list(nodepaths)
  #define names of each element in this list
  names(nodepaths) <- names(plots)
  
  #write plots 
  h <- length(itemNames) + 1
  mapply(function(X, Y){
    
    ggsave(filename = Y, plot = X,
           dpi = 600, width = 7.5, height = h, units = "cm")
    
  }, X = plots, Y = nodepaths )
  
  
  # Take observations with errors
  logs <- cbind( df[!keep,], expvar[!keep, ])
  # Transform this dataframe into a list
  logs <- apply(logs, 1,  as.list)
  
  # Add to list of outputs
  outputs <- list(
    coeff = mod_coeff, # table with coefficients from PL model (estimates, error, z-value),
    vars = as.list(names(expvar_i)), # name of explanatory vars used 
    tree = treepath, # the Plackett-Luce tree produced
    treenode = nodepaths, # the plots for each node produced
    nobs = as.list(nR), # number of observations used to analyse this characteristic
    logs = logs # dataframe with the observations not used for this analysis
  )
  
  results[[char_i]] <- outputs
  
  
}

#Make infosheets if required
if(infosheets){
  
  sheets <- vector(mode = "list", nrow(df))
  
  cat('Organising data for infosheets \n')
  
  #Copy trail data 
  df2 <- df
  
  #Get information for the header
  #it shows the observer name and the package id 
  header <- data.frame(cbind(techName = "ObserverName", 
                             aliasName = df[[ncol(pack)+1]], 
                             packId = df[[1]] ),
                       stringsAsFactors = FALSE)
  
  header <- apply(header, 1, as.list)
  
  #Get name of given items
  #it shows which items were given for the observer and how they where labeled (A,B,C)
  table1 <- apply(items, 1, function(X){
    
    Y <- data.frame(cbind(Item = colnames(items), Name = X), stringsAsFactors = FALSE)
    as.list(Y)
    
  })
  
  #Get table showing how each observer classified items
  #it shows how each observed ranked their given items from best to worst
  #first combine the rows from each third dimension in the array
  table2 <-  apply(R_all, 1, function(X){
    r <- t(X)
    r <- data.frame(r, stringsAsFactors = FALSE)
    rownames(r) <- char
    colnames(r) <- paste0("Position", seq_len(ncomp))
    r <- rownames_to_column(r, var = "Characteristic")
    r
  })
  #now each dimension in the array corresponds to one observer and 
  #each row to one characteristic
  #convert it into a list 
  table2 <- as.list(table2)
  #then into a list again
  table2 <- lapply(table2, function(X){
    apply(X, 1,  as.list)
  })
  
  
  #Get the overall rankings 
  #it shows how the items where ranked among the project considering all rankings provided
  table3 <- results$Overall$coeff
  table3 <- lapply( table3 , unlist)
  table3 <- do.call(rbind, table3)
  table3 <- cbind(Item = table3[,1], Position = rank((as.numeric(table3[,2]) -1) * - 1))
  table3 <- data.frame(table3, stringsAsFactors = FALSE)
  #drop local variety if exists
  table3 <- table3[!table3[,1] %in% "Local",]
  #update position
  table3[,2] <- rank(table3[,2])
  #sort values from position 1 to n
  table3 <- arrange(table3, table3[,2])
  table3 <- apply(table3, 1,  as.list)
  
  #Combine the lists per observer
  for(i in seq_along(rownames(df))){
    
    sheets[[i]] <- list(header = header[[i]], 
                        table1 = table1[[i]], 
                        table2 = table2[[i]],
                        table3 = table3)
  }
  
  #each element in this list corresponds to an observer
  #package id will be used to label it
  names(sheets) <- df$PackageID
  
  #add this list to results
  results$Infosheets <- sheets
  
}


#Convert it into json
output <- toJSON(results, pretty = TRUE, auto_unbox = TRUE)

#Write json file
write(output, paste0(pathname, "/", outputname))

cat("\n\nAll analysis done. Check your results here:", paste0(getwd(),"/", pathname), "\n")