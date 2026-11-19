from datetime import date
from dataset_definition import dataset


test_data = {
    # Expected in population - age 67 
    1: {
        "patients": {"date_of_birth": date(1956, 8, 1), "sex": "female"},
        "addresses": {
            "start_date": date(2015, 1, 1),
            "imd_rounded": 100,
            },
        "ons_deaths": [],
        "clinical_events": [
            {
                "snomedct_code": "154161000", # White British ethnic group
                "date": date(2015, 1, 1),
            },
            {
                "snomedct_code": "233602006", # rsv
                "date": date(2023,11,8),
            },
        ],
        "apcs": [
            {
                "admission_date": date(2022, 2, 15),
                "primary_diagnosis": "U071", # covid
            },
        ],
        "ethnicity_from_sus": [],
        "emergency_care_attendances": [],
        "practice_registrations": [
            {
                "start_date": date(2015, 1, 1),
                "practice_pseudo_id": 12345,
                "practice_systmone_go_live_date": date(2001,5,1),
            },
        ],
        "expected_in_population": True,
        "expected_columns": {
            "index_date": date(2023,9,1),
            "dereg_date": None,
            "ons_death_date": None,
            "end_fu": date(2024,8,31),
            "sex": "female",
            "age": 67,
            "age_group": "65-69",
            "ethnicity6_gp": "1",
            "ethnicity_sus": None,
            "imd_quintile": 1,
            "rsv_gp_date": date(2023,11,8),
            "rsv_sc_date": None,
            "rsv_emerg_date": None,
        },
    },
    # Not expected in population, age <65
    2: {
         "patients": {"date_of_birth": date(1996, 8, 1), "sex": "female"},
                "addresses": {
                    "start_date": date(2010, 1, 1),
                    "imd_rounded": 100,
                    },
                "ons_deaths": [],
                "clinical_events": [
                    {
                        "snomedct_code": "154161000", # White British ethnic group
                        "date": date(2015, 1, 1),
                    },
                    {
                        "snomedct_code": "233602006", # rsv
                        "date": date(2023,11,8),
                    },
                ],
                "apcs": [
                    {
                        "admission_date": date(2022, 2, 15),
                        "primary_diagnosis": "U071", # covid
                    },
                ],
                "ethnicity_from_sus": [],
                "emergency_care_attendances": [],
                "practice_registrations": [
                    {
                        "start_date": date(2010, 1, 1),
                        "practice_pseudo_id": 12345,
                        "practice_systmone_go_live_date": date(2001,5,1),
                    },
                ],
                "expected_in_population": False,
               
    },
    # Not expected in population, intersex
        3: {
             "patients": {"date_of_birth": date(1946, 8, 1), "sex": "intersex"},
                    "addresses": {
                        "start_date": date(1986, 1, 1),
                        "imd_rounded": 1001,
                        },
                    "ons_deaths": [],
                    "clinical_events": [
                        {
                            "snomedct_code": "154161000", # White British ethnic group
                            "date": date(2015, 1, 1),
                        },
                        
                    ],
                    "apcs": [
                        {
                            "admission_date": date(2022, 2, 15),
                            "primary_diagnosis": "U071", # covid
                        },
                    ],
                    "ethnicity_from_sus": [],
                    "emergency_care_attendances": [],
                    "practice_registrations": [
                        {
                            "start_date": date(2010, 1, 1),
                            "practice_pseudo_id": 12345,
                            "practice_systmone_go_live_date": date(2001,5,1),
                        },
                    ],
                    "expected_in_population": False,
                   
        },
    # Not expected in population, no IMD
        4: {
             "patients": {"date_of_birth": date(1936, 8, 1), "sex": "male"},
                    "addresses": {
                        "start_date": date(2018, 1, 1),
                        },
                    "ons_deaths": [],
                    "clinical_events": [
                        {
                            "snomedct_code": "154161000", # White British ethnic group
                            "date": date(2015, 1, 1),
                        },
                        {
                            "snomedct_code": "233602006", # rsv
                            "date": date(2023,11,8),
                        },
                    ],
                    "apcs": [
                        {
                            "admission_date": date(2022, 2, 15),
                            "primary_diagnosis": "U071", # covid
                        },
                    ],
                    "ethnicity_from_sus": [],
                    "emergency_care_attendances": [],
                    "practice_registrations": [
                        {
                            "start_date": date(2018, 1, 1),
                            "practice_pseudo_id": 12345,
                            "practice_systmone_go_live_date": date(2001,5,1),
                        },
                    ],
                    "expected_in_population": False,
                   
        },
    # Not expected in population, died prior to study start
        2: {
             "patients": {"date_of_birth": date(1936, 8, 1), "sex": "female"},
                    "addresses": {
                        "start_date": date(2010, 1, 1),
                        "imd_rounded": 1002,
                        },
                    "ons_deaths": [
                        {
                            "date": date(2022,12,6),
                        }
                    ],
                    "clinical_events": [
                        {
                            "snomedct_code": "154161000", # White British ethnic group
                            "date": date(2015, 1, 1),
                        },
                        {
                            "snomedct_code": "233602006", # rsv
                            "date": date(2022,11,8),
                        },
                    ],
                    "apcs": [
                        {
                            "admission_date": date(2022, 2, 15),
                            "primary_diagnosis": "U071", # covid
                        },
                    ],
                    "ethnicity_from_sus": [],
                    "emergency_care_attendances": [],
                    "practice_registrations": [
                        {
                            "start_date": date(2010, 1, 1),
                            "practice_pseudo_id": 12345,
                            "practice_systmone_go_live_date": date(2001,5,1),
                        },
                    ],
                    "expected_in_population": False,
                   
        },
    # Not expected in population, not registered
        2: {
             "patients": {"date_of_birth": date(1956, 8, 1), "sex": "female"},
                    "addresses": {
                        "start_date": date(2024, 12, 1),
                        "imd_rounded": 100,
                        },
                    "ons_deaths": [],
                    "clinical_events": [
                        {
                            "snomedct_code": "154161000", # White British ethnic group
                            "date": date(2015, 1, 1),
                        },
                        {
                            "snomedct_code": "233602006", # rsv
                            "date": date(2023,11,8),
                        },
                    ],
                    "apcs": [
                        {
                            "admission_date": date(2022, 2, 15),
                            "primary_diagnosis": "U071", # covid
                        },
                    ],
                    "ethnicity_from_sus": [],
                    "emergency_care_attendances": [],
                    "practice_registrations": [
                        {
                            "start_date": date(2024, 12, 1),
                            "practice_pseudo_id": 12345,
                            "practice_systmone_go_live_date": date(2001,5,1),
                        },
                    ],
                    "expected_in_population": False,
                   
        },
}