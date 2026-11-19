library(tidyverse)
library(here)
library(arrow)

outdir <- here("output", "tables")
fs::dir_create(outdir)

data_clean <- read_feather(here("output/an_dataset_clean.arrow")) 
capture.output(
  skimr::skim_without_charts(data_clean),
  file = here(outdir, paste0("skim_clean.txt")),
  split=FALSE
)