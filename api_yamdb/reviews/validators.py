from datetime import datetime as dt

import api.exceptions as ApiException


def validate_year(value):
    year = dt.now()
    if not 0 < value <= year.year:
        raise ApiException.YearValidationError
    return value
