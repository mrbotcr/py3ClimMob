# Jacob van Etten
# Bioversity International
# Improved version, September 2017

# Script to generate designs for ranking of options
# It is designed for tricot trials specifically (comparing 3 options)
# But it will also work with comparisons of any other number of options
# The design strives for approximate A optimality
# This means that it is robust to missing observations
# It also strives for balance for positions of each option
# Options are equally divided between first, second, third, etc. position
# The script works with any number of options, observers
# sudo apt-get install r-cran-rcppeigen

if (!require("Matrix"))
{
        install.packages("Matrix",repos="http://cran.rstudio.com/")
}
if (!require("methods"))
{
        install.packages("methods",repos="http://cran.rstudio.com/")
}
if (!require("rARPACK"))
{
        install.packages("rARPACK",repos="http://cran.rstudio.com/")
}
require(Matrix)
require(methods)
require(rARPACK)
require(stringr)

# Define function for Kirchhoff index
# This index determines which graph is connected in the most balanced way
# In this context, lower values (lower resistance) is better

KirchhoffIndex <- function(x){
  
  # The input matrix only has one triangle filled
  # First we make it symmetric
  x <- x + t(x) 
  
  # Then some maths to get the Kirchhoff index
  
  # Using rARPACK:eigs
  Laplacian <- as(Diagonal(x=colSums(x)) - x, "dsyMatrix")
  lambda <- try(eigs(Laplacian, k=(dim(Laplacian)[1]-1), retvec=FALSE)$values, silent=TRUE)
  if(class(lambda) == "try-error"){r <- Inf} else {r <- sum(1/lambda)}
  
  # Supposedly slower with base:eigen
  # lambda <- eigen(Laplacian)$values
  # lambda <- lambda[-length(lambda)]
  
  return(r)
  
}

# get all permutations

getPerms <- function(x) {
  if (length(x) == 1) {
    return(x)
  }
  else {
    res <- matrix(nrow = 0, ncol = length(x))
    for (i in seq_along(x)) {
      res <- rbind(res, cbind(x[i], Recall(x[-i])))
    }
    return(res)
  }
}

# Shannon (as evenness measure)
shannon <- function(x) sum(ifelse(x==0, 0, x*log(x)))

# Get Shannon index for order positions
getShannonMatrix <- function(x){
  
  pp <- position * 0 
  pp[cbind(x,1:length(x))] <- 1
  pp <- position + pp
  return(shannon(as.vector(pp)))

}

getShannonVector <- function(x) {
  
  xi <- rep(0, times=nvar)
  xi[x] <- 1
  return(shannon(sumcomb + xi))
  
}

# Get the arguments
args <- commandArgs(trailingOnly = TRUE)
filename <- args[1]

fin <- file(filename,open="r")

# First line is the number of items each observer receives
nitems <- as.integer(readLines(fin, n = 1, warn = FALSE))
# Second line is the number of observers
nobservers <- as.integer(readLines(fin, n = 1, warn = FALSE))
# Third line is the number of diferent varieties
nvar <- as.integer(readLines(fin, n = 1, warn = FALSE))

# Create an empty vector to keep the varieties
itemnames <- c()

# Loop over the the number of varieties, get the names and put them into the vector
for (i in 1:nvar){
  itemnames <- c(itemnames,readLines(fin, n = 1, warn = FALSE))
}

# Close the file 
close(fin)

# For testing without external file, uncomment the following lines
#nitems <- 3
#nobservers <- 1000
#nvar <- 15
#itemnames <- paste("Var", 1:nvar, sep="")

# Varieties indicated by integers
varieties <- 1:nvar    

# Full set of all combinations
varcombinations <- t((combn(varieties, nitems)))

# if the full set of combinations is small and can be covered at least once
# the set will include each combination at least once
ncomb <- dim(varcombinations)[1]
n <- floor(nobservers/ncomb)
nfixed <- ncomb*n
vars1 <- varcombinations[c(rep(1:(dim(varcombinations)[1]), times=n)),]

# the remaining combinations are sampled randomly but in a balanced way
# this means that no combination enters more than once
nremain <- nobservers-nfixed

#create set to get to full number of observers
vars2 <- matrix(nrow=nremain,ncol=nitems)

# set up array with set of combinations
varcomb <- matrix(0, nrow=nvar, ncol=nvar)

if(dim(vars2)[1]>0.5){
  
  # select combinations for the vars2 set that optimize design
  for(i in 1:nremain){
    
    # calculate frequency of each variety
    sumcomb <- rowSums(varcomb) + colSums(varcomb)

    # priority of each combination is equal to Shannon index of varieties in each combination
    prioritycomb <- apply(varcombinations, 1, getShannonVector)

    # highest priority to be selected is the combination which has the lowest Shannon index
    selected <- which(prioritycomb == min(prioritycomb))
    
    # if there are ties, find out which combination reduces Kirchhoff index most 
    
    if(length(selected) > 1 & i > 25){
      
      # randomly subsample from selected if there are too many combinations to check
      if(length(selected) > 10) selected <- sample(selected, 10)
      
      # get a nvar x nvar matrix with number of connections
      
      # calculate Kirchhoff index and select smallest value
      khi <- vector(length=length(selected))
      for(k in 1:length(selected)){
        
        evalgraph <- varcomb
        index <- t(combn(varcombinations[selected[k],], 2))
        evalgraph[index] <- evalgraph[index] + 1 
        khi[k] <- KirchhoffIndex(evalgraph)
        
      } 
      
      print(khi)
      selected <- selected[which(khi == min(khi))]
    
    }
    
    # if there are still ties between ranks of combinations, selected randomly from the ties
    if(length(selected) > 1) selected <- sample(selected, 1)
    
    # assign the selected combination
    vars2[i,] <- varcombinations[selected,]
    varcomb[t(combn(varcombinations[selected,],2))] <- varcomb[t(combn(varcombinations[selected,],2))] + 1
    
    # remove used combination
    varcombinations <- varcombinations[-selected,]
      
  }
}

# merge vars1 and vars2 to create the full set of combinations
vars <- rbind(vars1, vars2)

# create empy object to contain ordered combinations of vars
varOrdered <- matrix(NA, nrow=nobservers, ncol=nitems)

# set up array with set of combinations
varcomb <- matrix(0, nrow=nvar, ncol=nvar)

# fill first row
selected <- sample(1:nobservers, 1)
varcomb[t(combn(vars[selected,],2))] <- 1
varOrdered[1,] <- vars[selected,]
vars <- vars[-selected,]

# optimize the order of overall design by repeating a similar procedure to the above
for(i in 2:(nobservers-1)){
  
  # calculate frequency of each variety
  sumcomb <- rowSums(varcomb) + colSums(varcomb)
  
  # priority of each combination is equal to Shannon index of varieties in each combination
  prioritycomb <- apply(vars, 1, getShannonVector) 
  
  # highest priority to be selected is the combination which has the lowest Shannon index
  selected <- which(prioritycomb == min(prioritycomb))
  
  # if there are ties, find out which combination reduces Kirchhoff index most 
  if(length(selected) > 1 & i > 25){
    
    # randomly subsample from selected if there are too many combinations to check
    if(length(selected) > 10) selected <- sample(selected, 10)
    
    # get a nvar x nvar matrix with number of connections
    sumcombMatrix <- varcomb * 0
    
    # in this case, get matrix to calculate Kirchhoff index only for last 10 observers
    for(j in max(1,i-10):(i-1)){
      
      index <- t(combn(varOrdered[j,],2))
      sumcombMatrix[index] <- sumcombMatrix[index] + 1
    
    }
      
    # calculate Kirchhoff indices for the candidate matrix corresponding to each row in selected
    khi <- vector(length=length(selected))
    for(k in 1:length(selected)){
      
      evalgraph <- sumcombMatrix
      index <- t(combn(vars[selected[k],], 2))
      evalgraph[index] <- evalgraph[index] + 1 
      khi[k] <- KirchhoffIndex(evalgraph)
      
    } 
    
    print(khi)
    # select combination that produces the lowest Kirchhoff index
    selected <- selected[which(khi == min(khi, na.rm=TRUE))]
    
  }
  
  # if there are still ties between ranks of combinations, select one randomly 
  if(length(selected) > 1) selected <- selected[sample(1:length(selected), 1)]
  
  # assign the selected combination
  varOrdered[i,] <- vars[selected,]
  varcomb[t(combn(vars[selected,],2))] <- varcomb[t(combn(vars[selected,],2))] + 1
  
  # remove used combination
  vars <- vars[-selected,]
  
}

# assign last one
varOrdered[nobservers,] <- vars

# Equally distribute positions, e.g. order balance
# First create matrix with frequency of position of each of nvar
position <- matrix(0, ncol=nitems, nrow=nvar)

# Sequentially reorder sets to achieve evenness in positions
# Shannon is good here, because evenness values are proportional
# the H denominator in the Shannon formula is the same

for(i in 1:nobservers){
  
  varOrdered_all <- getPerms(varOrdered[i,])
  varOrdered_Shannon <- apply(varOrdered_all, 1, getShannonMatrix)
  varOrdered_i <- varOrdered_all[which(varOrdered_Shannon == min(varOrdered_Shannon))[1],]
  varOrdered[i,] <- varOrdered_i
  pp <- position * 0 
  pp[cbind(varOrdered_i,1:nitems)] <- 1
  position <- position + pp
  
}
  
# The varOrdered matrix has the indices of the elements 
# Create the final matrix
finalresults <- matrix(NA,ncol=nitems,nrow=nobservers)

# loop over the rows and columns of the final matrix and put the elements randomized
# with the indexes in varOrdered
for (i in 1:nobservers){
  for (j in 1:nitems){
    finalresults[i,j] <- itemnames[varOrdered[i,j]]
  }
}

# write the results to a file
file_without_ext <- str_sub(filename,1,nchar(filename)-4)
write.table(finalresults,file=paste(file_without_ext,"_2.txt",sep=""),row.names=FALSE,col.names=FALSE,sep="\t")
