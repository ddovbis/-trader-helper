from datetime import datetime, timedelta


def obj_to_str(obj, exclude: list = []):
    """
    Transforms object to a string representation
    :param obj: object to transform
    :param exclude: a list of parameters that should be excluded from the result
    :return: string representation of the object
    """
    obj_var_values = [f"{name}={attr}" for name, attr in vars(obj).items() if not name.startswith("__") and name not in exclude]
    return f"{type(obj).__name__}({', '.join(obj_var_values)})"


def add_time_to_str_date(date: str, date_format: str, to_add: timedelta) -> str:
    """
    Converts string date into a date format
    Adds provided timedelta to the date
    Converts resulted date back into string

    :param date: original date
    :param date_format: format of the original date, also used for the return format, e.g. "YYYY-MM-DD"
    :param to_add: timedelta to add to the date
    :return: original date + timedelta
    """
    date = datetime.strptime(date, date_format)
    modified_date = date + to_add
    return datetime.strftime(modified_date, date_format)


def extract_time_from_str_date(date: str, date_format: str, to_extract: timedelta) -> str:
    """
    Converts string date into a date format
    Extracts provided timedelta from the date
    Converts resulted date back into string

    :param date: original date
    :param date_format: format of the
    original date, also used for the return format, e.g. "YYYY-MM-DD"
    :param to_extract: timedelta to extract from the date
    :return: original date - timedelta
    """
    date = datetime.strptime(date, date_format)
    modified_date = date - to_extract
    return datetime.strftime(modified_date, date_format)


def format_currency_value(value: float):
    if value > 100:
        return int(value)
    else:
        return "{:.2f}".format(value)


def format_percentage(percentage: float):
    return "{:.2f}".format(percentage)
