library(here)
library(tidyverse)
library(arrow)
library(lubridate)
library(readr)
library(gtsummary)

## Import custom user functions
source(here::here("analysis", "redaction.R"))

outdir <- here("output", "tables")
fs::dir_create(outdir)

# Stat column names and their group labels from a tbl_summary, for redaction
stat_headers <- function(tbl) {
  tbl$table_styling$header %>%
    filter(str_detect(column, "^stat_\\d+$")) %>%
    mutate(label = if_else(column == "stat_0", "Overall", label))
}

# Import and format ethnicity into one variable
cr_data <- read_feather("output/dataset.arrow") %>% 
    mutate(
        ethnicity6_from_codes = relevel(factor(ethnicity6_gp,
                                     levels = c("1", "2", "3", "4", "5"),
                                     labels = c("White", "Mixed",
                                                "Asian or Asian British",
                                                "Black or Black British",
                                                "Other Ethnic Groups"),
                                     ordered = FALSE), ref = "White"),
        ethnicity6_from_sus = relevel(factor(recode(
                    ethnicity_sus, "A" = "White", "B" = "White", "C" = "White",
                    "D" = "Mixed", "E" = "Mixed", "F" = "Mixed", "G" = "Mixed",
                    "H" = "Asian or Asian British", "J" = "Asian or Asian British",
                    "K" = "Asian or Asian British", "L" = "Asian or Asian British",
                    "M" = "Black or Black British", "N" = "Black or Black British",
                    "P" = "Black or Black British", "R" = "Other Ethnic Groups",
                    "S" = "Other Ethnic Groups"), ordered = F), ref = "White"),
        ethnicity6_combined = if_else(
                is.na(ethnicity6_from_codes), if_else(is.na(ethnicity6_from_sus), "Unknown", ethnicity6_from_sus), 
                ethnicity6_from_codes
        ),
        days_fu = (end_fu - index_date),
        rsv_gp = !is.na(rsv_gp_date) & rsv_gp_date <= end_fu,
        rsv_sc = !is.na(rsv_sc_date) & rsv_sc_date <= end_fu,
        rsv_emerg = !is.na(rsv_emerg_date) & rsv_emerg_date <= end_fu,
        end_rsv_gp = pmin(end_fu, rsv_gp_date, na.rm = TRUE),
        end_rsv_sc = pmin(end_fu, rsv_sc_date, na.rm = TRUE),
        end_rsv_emerg = pmin(end_fu, rsv_emerg_date, na.rm = TRUE),
        time_rsv_gp = as.numeric(end_rsv_gp - index_date),
        time_rsv_sc = as.numeric(end_rsv_sc - index_date),
        time_rsv_emerg = as.numeric(end_rsv_emerg - index_date)
    )

write_feather(cr_data, here("output", "an_dataset_clean.arrow"))

# Generate baseline table
baseline_table <- cr_data %>%
    select(age, age_group, sex, ethnicity6_combined, imd_quintile) %>%
     mutate(ethnicity6_combined = fct_na_value_to_level(
                ethnicity6_combined, 
                level = "Missing")) %>%
    tbl_summary(
                missing = "no",
                by = imd_quintile
        ) %>% 
        add_overall(last = FALSE) %>% 
        modify_header(
            label ~ "Characteristic",
            stat_0 ~ "Overall",
            all_stat_cols(stat_0 = FALSE) ~ "IMD quintile {level}"
        )

headers <- stat_headers(baseline_table)        
# # Apply redactions to baseline table
baseline_table_redact_round <- fn_redact_tbl_summary(
        tbl_summary = baseline_table, 
        threshold = 7,
        col_names  = headers$column,
        rename_cols = headers$label
        ) 

write_csv(as_tibble(baseline_table), here(outdir, "baseline_table.csv"))
write_csv(as_tibble(baseline_table_redact_round), here(outdir, "baseline_table_r.csv"))

# Generate table of rates by age and IMD
# GP
rates_gp <- cr_data %>%
group_by(age_group, imd_quintile) %>%
summarise(
    n = n(),
    gp_events = sum(rsv_gp),
    person_years_gp = sum(time_rsv_gp) / 365.25,
    rate_gp_per_1000 = 1000 * gp_events / person_years_gp,
    .groups = "drop"
)

# Hospital admissions
rates_sc <- cr_data %>%
group_by(age_group, imd_quintile) %>%
summarise(
    n = n(),
    sc_events = sum(rsv_sc),
    person_years_sc = sum(time_rsv_sc) / 365.25,
    rate_sc_per_1000 = 1000 * sc_events / person_years_sc,
    .groups = "drop"
)

# A & E
rates_emerg <- cr_data %>%
group_by(age_group, imd_quintile) %>%
summarise(
    n = n(),
    emerg_events = sum(rsv_emerg),
    person_years_emerg = sum(time_rsv_emerg) / 365.25,
    rate_emerg_per_1000 = 1000 * emerg_events / person_years_emerg,
    .groups = "drop"
)

# redact and round
rates_gp_round <- rates_gp %>%
    mutate(
      n_mid6 = if_else(n <= 7, NA_real_, roundmid_any(n)),
      gp_events_mid6 = if_else(gp_events <= 7, NA_real_, roundmid_any(gp_events)),
      person_years_gp_mid6 = if_else(person_years_gp <= 7,
                                 NA_real_,
                                 roundmid_any(person_years_gp)),
      gp_rate_mid6 = round(
        (gp_events_mid6 / person_years_gp_mid6) * 1000,
        5
      )
    ) %>% 
    select(-n, -gp_events, -person_years_gp)

write_csv(as_tibble(rates_gp), here(outdir, "rates_gp.csv"))
write_csv(as_tibble(rates_sc), here(outdir, "rates_sc.csv"))
write_csv(as_tibble(rates_emerg), here(outdir, "rates_emerg.csv"))

write_csv(as_tibble(rates_gp_round), here(outdir, "rates_gp_r.csv"))