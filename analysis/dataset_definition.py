from datetime import date
from ehrql import create_dataset, case, when, maximum_of, minimum_of, years
from ehrql.tables.tpp import (
  patients,
  ons_deaths,
  addresses,
  clinical_events,
  practice_registrations,
  apcs,
  emergency_care_attendances,
  ethnicity_from_sus, 
)

import codelists

from variable_lib import (
  emergency_care_diagnosis_matches
)

study_start_date = "2023-09-01"
study_end_date = "2024-08-31"

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000, additional_population_constraint = (((practice_registrations.for_patient_on(study_start_date).end_date)>(study_start_date)) | (practice_registrations.for_patient_on(study_start_date).end_date.is_null())) & (((ons_deaths.date)>(study_start_date)) | (ons_deaths.date.is_null())))

## Inclusion criteria
# Age 65 or over
# date age 65
age_65 = patients.date_of_birth + years(65)
# latest of study start or when 65
index_age_date = case(
    when(age_65.is_before(study_end_date)).then(maximum_of(study_start_date, age_65))
)
# age between 0 and 110 and not missing
age = patients.age_on(index_age_date)
valid_age = (age >=65) & (age <= 100)
# Alive at latest of study start or when 65
was_alive = ((ons_deaths.date.is_after(index_age_date) | ons_deaths.date.is_null()))
# Registered at latest of study start or when 65
was_registered = practice_registrations.for_patient_on(index_age_date).exists_for_patient()
# known sex
has_known_sex = patients.sex.is_in(["female", "male"])
# known IMD
has_known_imd = addresses.for_patient_on(index_age_date).imd_rounded.is_not_null() 
# lives in a care home at latest of study start or when 65
living_carehome = (
        addresses.for_patient_on(index_age_date).care_home_is_potential_match |
        addresses.for_patient_on(index_age_date).care_home_requires_nursing |
        addresses.for_patient_on(index_age_date).care_home_does_not_require_nursing
    ).when_null_then(False)

dataset.define_population(
    age_65.is_before(study_end_date)
    & was_alive
    & was_registered
    & has_known_sex
    & valid_age
    & has_known_imd
    & ~ living_carehome 
    )

# Variables required in dataset
# Information for follow-up 
dataset.index_date = index_age_date
# End follow-up at end of study period, death, deregistration, age 100
dataset.dereg_date = (
  (practice_registrations.for_patient_on(dataset.index_date)).end_date
)
dataset.ons_death_date = ons_deaths.date
age_100 = patients.date_of_birth + years(100)
dataset.end_fu = minimum_of(study_end_date, dataset.dereg_date, dataset.ons_death_date, age_100)
# Other variables
#IMD
imd_rounded = addresses.for_patient_on(dataset.index_date).imd_rounded
max_imd = 32844
 
dataset.imd_quintile = case(
    when((imd_rounded >= 0) & (imd_rounded <= int(max_imd * 1 / 5))).then(1),
    when(imd_rounded <= int(max_imd * 2 / 5)).then(2),
    when(imd_rounded <= int(max_imd * 3 / 5)).then(3),
    when(imd_rounded <= int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
    otherwise = 99
    )
# Age
dataset.age = patients.age_on(dataset.index_date)
dataset.age_group = case(
    when((dataset.age >= 65) & (dataset.age < 70)).then("65-69"),
    when((dataset.age >= 70) & (dataset.age < 75)).then("70-74"),
    when((dataset.age >= 75) & (dataset.age < 80)).then("75-79"),
    when((dataset.age >= 80) & (dataset.age < 85)).then("80-84"),
    when((dataset.age >= 85) & (dataset.age < 90)).then("85-89"),
    when((dataset.age >= 90) & (dataset.age < 100)).then("90+")
)
# Sex
dataset.sex = patients.sex
# Ethnicity - GP and secondary care
dataset.ethnicity6_gp = (
   clinical_events.where(clinical_events.snomedct_code.is_in(codelists.ethnicity6_codes))
    .where(clinical_events.date.is_on_or_before(dataset.index_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code.to_category(codelists.ethnicity6_codes)
)

dataset.ethnicity_sus = ethnicity_from_sus.code

# RSV - primary care
dataset.rsv_gp_date = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.rsv_primary_codelist)
).where(clinical_events.date.is_on_or_between(dataset.index_date,study_end_date)).date.minimum_for_patient()

dataset.rsv_sc_date = apcs.where(
    (apcs.primary_diagnosis.is_in(codelists.rsv_secondary_codelist)) | (apcs.secondary_diagnosis.is_in(codelists.rsv_secondary_codelist))
).where(apcs.admission_date.is_on_or_between(dataset.index_date,study_end_date)).admission_date.minimum_for_patient()

dataset.rsv_emerg_date = emergency_care_diagnosis_matches(emergency_care_attendances, codelists.rsv_attendance).where(
       emergency_care_attendances.arrival_date
        .is_on_or_between(dataset.index_date, study_end_date)).where(
            emergency_care_attendances.discharge_destination.is_in(codelists.discharge_home)).arrival_date.minimum_for_patient()