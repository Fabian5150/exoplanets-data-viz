install.packages("dplyr")

library(ggplot2)
library(dplyr)

# Take a look at all datasets. If needed merge multiple ones
# Create nice visualisations to compare size and distance to earth

# from http://exoplanets.org/table
exo <- read.csv("gitProjects/uni/dataviz/r/playground/data/RIAZFPNI.csv", header=TRUE)

# from https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS&constraint=default_flag=1&constraint=disc_facility+like+%27%25TESS%25%27
# (confirmed planets only)
nasa <- read.csv(
  "gitProjects/uni/dataviz/r/playground/data/PS_2025.02.18_01.36.05.csv",
  comment.char="#", stringsAsFactors=FALSE
)

# Only planets no controversy about their existence
# TBD: Also check column "solution type"
nasa <- subset(nasa, pl_controv_flag == 0)

# What to do? Decide on subset of parameters to take into account
# Find reliable data for those same values for earth, to get a comparison
# Nasa Dataset as already a few columns where the value is just a factor of the earth's value :)
# Questions:
  # How to retrieve the ~5 most important parameters to look at DATA-DRIVEN?

colSums(is.na(nasa))
colnames(nasa)

# Check for duplicates 👀
print(sum(duplicated(nasa$pl_name)))
# => A lot of duplicates. Probably different observations of the same planet
#     How can they be merged? averages / majority votes of values?

# TBD: Filter for only 'interesting' columns and figure out, how many missing values there are
range(nasa$pl_rade, na.rm = TRUE)
range(nasa$pl_masse, na.rm = TRUE)
range(nasa$pl_eqt, na.rm = TRUE)

sum(is.na(nasa$pl_rade))
sum(is.na(nasa$pl_masse)) # => Mostly na :/
sum(is.na(nasa$pl_eqt))


# Histogram of Temperature
temp_num <- subset(nasa, is.numeric(pl_eqt))
temp_num$pl_eqt = temp_num$pl_eqt + 273.15
hist(temp_num$pl_eqt, xlab="Equilibrium Temperature (°C)")

# Boxplot of Temperature
ggplot(temp_num, aes(y=pl_eqt)) +
  geom_boxplot() +
  labs(x="Equilibirum Tempereature")

temp_num_liveable = subset(temp_num, (pl_eqt > -50 & pl_eqt < 400))
nrow(temp_num_liveable)

# Scatterplot of factors for planet radius and mass to earth measures:
ggplot(subset(nasa, is.numeric(pl_masse)), aes(x = pl_rade, y = pl_masse)) +
  geom_point(size = 1) +
  labs(y = "Factor of Earth's Mass", x = "Factor of Earth's Radius")
