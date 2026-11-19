# Import libraries ----
library('tidyverse')
library('lubridate')

#define function for midpoint 6 rounding
roundmid_any <- function(x, to = 6) {
  
  # like round_any, but centers on (integer) midpoint of the rounding points
  ceiling(x/to)*to - (floor(to/2)*(x != 0))
  
}

# taken from ckd-coverage-ve
redactor <- function(n, threshold){

  # given a vector of frequencies, this returns a boolean vector that is TRUE if
  # a) the frequency is <= the redaction threshold and
  # b) if the sum of redacted frequencies in a) is still <= the threshold, then the
  # next largest frequency is also redacted

  n <- as.integer(n)
  leq_threshold <- dplyr::between(n, 1, threshold)
  n_sum <- sum(n)

  # redact if n is less than or equal to redaction threshold
  redact <- leq_threshold

  # also redact next smallest n if sum of redacted n is still less than or equal to threshold
  if((sum(n*leq_threshold) <= threshold) & any(leq_threshold)){
    redact[which.min(dplyr::if_else(leq_threshold, n_sum+1L, n))] = TRUE
  }

  redact
}


redactor2 <- function(n, threshold=5, x=NULL){

  # given a vector of frequencies (n), this returns a redacted vector (if x is NULL) or
  # reaction of a secondary vector based on frequencies in the first (if x is not nULL).
  # using the following rules:
  # a) the frequency is <= the redaction threshold and
  # b) if the sum of redacted frequencies in a) is still <= the threshold, then the
  # next largest frequency is also redacted


  stopifnot("n must be non-missing" = all(!is.na(n)))
  stopifnot("n must non-negative" = all(n>=0))

  if(is.null(x)){
    x <- n
  } else {
    stopifnot("x must be same length as n" = length(n) == length(x))
  }

  n <- as.integer(n)
  leq_threshold <- dplyr::between(n, 1, threshold)
  n_sum <- sum(n)

  # redact if n is less than or equal to redaction threshold
  redact <- leq_threshold

  # also redact next smallest n if sum of redacted n is still less than or equal to threshold
  if((sum(n*leq_threshold) <= threshold) & any(leq_threshold)){
    redact[which.min(dplyr::if_else(leq_threshold, n_sum+1L, n))] = TRUE
  }


  typedNA <- NA
  mode(typedNA) <- typeof(x)

  redacted <- dplyr::if_else(redact, typedNA, x)

  redacted
}

# Copied from metformin_covid repo
################################################################################
# Custom made function to round a tbl_summary object, it does the following:
# Take a tbl_summary() object as input and a threshold for redaction
# Redact categorical/dichotomous counts, including the total column total (second row N Total)
# Recalculate percentages for subgroup rows, based on the redacted column total
# Leave continuous variables untouched
# Return a clean tibble with renamed columns
## CAVE: inside uses the general midpoint rounding function: fn_roundmid_any
################################################################################
library(dplyr)
library(stringr)
library(purrr)
library(tidyr)

fn_redact_tbl_summary <- function(tbl_summary_obj, 
                                  threshold = 6,
                                  col_names = c("stat_1", "stat_2"),
                                  rename_cols = c("group1", "group2")) {
  
  # Step 0: extract table body as tibble
  tbl_df <- as_tibble(tbl_summary_obj$table_body)
  
  # Step 1: round counts for categorical/dichotomous rows
  # takes off percentage in brackets and rounds all numbers (regardless of whether will be redacted or not)
  tbl_df <- tbl_df %>%
    mutate(
      across(
        all_of(col_names),
        ~ ifelse(
          var_type %in% c("categorical", "dichotomous"),
          map_chr(.x, function(cell) {
            if (is.na(cell) || cell == "") return(cell)
            txt <- str_replace_all(cell, ",", "")
            txt <- str_trim(txt)
            count <- suppressWarnings(as.numeric(str_extract(txt, "^[0-9]+")))
            if (is.na(count)) return(cell)
            ifelse(count <=threshold, NA_real_, roundmid_any(count)) %>% as.character()
          }),
          .x
        )
      )
    )
  
  # Step 2: extract numeric counts dynamically
  count_col_names <- paste0(col_names, "_count")
  
  for (i in seq_along(col_names)) {
    tbl_df[[count_col_names[i]]] <- tbl_df[[col_names[i]]] %>%
      str_remove_all(",") %>%
      str_extract("^[0-9]+") %>%
      as.numeric()
  }
  
  # Step 3: get redacted totals dynamically
  # totals <- sapply(count_col_names, function(count_col) {
  #   tbl_df %>%
  #     filter(var_label == "Overall" & var_type == "categorical" & row_type == "level") %>%
  #     pull(count_col) %>%
  #     as.numeric()
  # })
  
  # Step 4: recalc percentages dynamically
  print("stat_0_count" %in% names(tbl_df))
  overall_counts <- tbl_df[["stat_0_count"]]  # extract once outside the loop

  for (i in seq_along(col_names)) {
    count_col <- count_col_names[i]
    #total     <- totals[i]
    
    tbl_df <- tbl_df %>%
      mutate(
        !!col_names[i] := ifelse(
          var_type %in% c("categorical", "dichotomous") &
            !var_label %in% c("Total N", "N") &
            !is.na(.data[[count_col]]),
          paste0(
            formatC(.data[[count_col]], format = "f", digits = 0, big.mark = ","),
            " (", round(100 * .data[[count_col]] / overall_counts, 1), "%)"
          ),
          !!sym(col_names[i])
        )
      )
  }
  
  # Drop count columns
  tbl_df <- tbl_df %>%
    select(-all_of(count_col_names))
  
  # Step 5: rename dynamically
  rename_mapping <- setNames(col_names, rename_cols[seq_along(col_names)])
  tbl_df <- tbl_df %>%
    rename(!!!rename_mapping)
  
  return(tbl_df)
}