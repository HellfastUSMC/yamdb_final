from datetime import datetime as dt

import api.exceptions as api_exception


def validate_year(value):
    year = dt.now()
    if not 0 < value <= year.year:
        raise api_exception.YearValidationError
    return value
