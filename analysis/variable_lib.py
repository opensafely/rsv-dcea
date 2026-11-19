import operator
from functools import reduce

def any_of(conditions):
    return reduce(operator.or_, conditions)

def emergency_care_diagnosis_matches(emergency_care_attendances, codelist):
    conditions = [
        getattr(emergency_care_attendances, column_name).is_in(codelist)
        for column_name in [f"diagnosis_{i:02d}" for i in range(1, 3)]
    ]
    return emergency_care_attendances.where(any_of(conditions))
