from datetime import datetime, timedelta

from pandas import Timestamp


def obj_to_str(obj, exclude: list = None):
    """
    Transforms object to a string representation
    :param obj: object to transform
    :param exclude: a list of parameters that should be excluded from the result
    :return: string representation of the object
    """
    if exclude is None:
        exclude = []

    obj_var_values = [f"{name}={attr}" for name, attr in vars(obj).items() if not name.startswith("__") and name not in exclude]
    return f"{type(obj).__name__}({', '.join(obj_var_values)})"


def get_timedelta(units, interval):
    if interval == "1d":
        return timedelta(days=units)
    else:
        raise NotImplementedError()


def add_time_and_convert_to_string(timestamp: Timestamp, date_format: str, to_add: timedelta) -> str:
    """
    Adds provided timedelta to the date
    Converts resulted date into string

    :param timestamp: original timestamp
    :param date_format: format of the date to return, e.g. "YYYY-MM-DD"
    :param to_add: timedelta to add to the date
    :return: original date + timedelta
    """
    modified_date = timestamp + to_add
    return datetime.strftime(modified_date, date_format)


def extract_time_and_convert_to_string(date: Timestamp, date_format: str, to_extract: timedelta) -> str:
    """
    Extracts provided timedelta from the date
    Converts resulted date into string

    :param date: original date
    :param date_format: format of the date to return, e.g. "YYYY-MM-DD"
    :param to_extract: timedelta to extract from the date
    :return: original date - timedelta
    """
    modified_date = date - to_extract
    return datetime.strftime(modified_date, date_format)


def format_currency_value(value: float):
    if value > 100:
        return int(value)
    else:
        return "{:.2f}".format(value)


def format_percentage(percentage: float):
    return "{:.2f}".format(percentage)
