# import ehrql function for importing codelists
from ehrql import (
  codelist_from_csv
)

#expand codes in SUS which are 3 characters to have X at the end
def expand_three_char_icd10_codes(codelist):
    return codelist + [f"{code}X" for code in codelist if len(code) == 3]

# ethnicity codes
ethnicity6_codes = codelist_from_csv(
  "codelists/opensafely-ethnicity-snomed-0removed.csv",
  column = "code",
  category_column = "Grouping_6",
)
# rsv primary - specific 
rsv_primary_codelist = codelist_from_csv(
  "codelists/opensafely-rsv-identification-primary-care.csv",
  column = "code",
)
# rsv secondary - specific
rsv_secondary_codelist = codelist_from_csv(
  "codelists/opensafely-rsv-identification-secondary-care.csv",
  column = "code",
)
rsv_secondary_codelist = expand_three_char_icd10_codes(rsv_secondary_codelist)
# rsv emergency attendances - specific
rsv_attendance = ["50417007"]
discharge_home = ["306689006"]
