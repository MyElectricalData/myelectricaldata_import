"""This module contains dependencies for the application."""
import logging
from datetime import datetime, timedelta
from math import floor
from os import environ, getenv

import pytz
from art import decor, text2art
from dateutil.parser import parse

from __version__ import VERSION

if environ.get("APPLICATION_PATH") is None:
    APPLICATION_PATH = "/app"
else:
    APPLICATION_PATH = environ.get("APPLICATION_PATH")

if environ.get("APPLICATION_PATH_DATA") is None:
    APPLICATION_PATH_DATA = "/data"
else:
    APPLICATION_PATH_DATA = getenv("APPLICATION_PATH_DATA")

if environ.get("APPLICATION_PATH_LOG") is None:
    APPLICATION_PATH_LOG = "/log"
else:
    APPLICATION_PATH_LOG = getenv("APPLICATION_PATH_LOG")


def daterange(start_date, end_date):
    """Generate a range of dates between the start_date and end_date.

    Args:
        start_date (datetime.date): The start date of the range.
        end_date (datetime.date): The end date of the range.

    Yields:
        datetime.date: The dates in the range.

    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def is_bool(v):
    """Check if a value is a boolean.

    Args:
        v (any): The value to check.

    Returns:
        bool: True if the value is a boolean, False otherwise.

    """
    if v in ["true", "false", "yes, no", "t, f", "y, n", 1, 0]:
        return True
    return False


def str2bool(v):
    """Convert a string representation of a boolean value to a boolean.

    Args:
        v (str): The string representation of the boolean value.

    Returns:
        bool: The boolean value.

    """
    if not isinstance(v, bool):
        return v and v.lower() in ("yes", "true", "t", "1")
    return v


def is_float(element):
    """Check if a value can be converted to a float.

    Args:
        element (any): The value to check.

    Returns:
        bool: True if the value can be converted to a float, False otherwise.

    """
    try:
        float(element)
        return True
    except ValueError:
        return False


def is_datetime(element, fuzzy=False):
    """Check if a value can be parsed as a datetime.

    Args:
        element (str): The value to check.
        fuzzy (bool, optional): Whether to allow fuzzy parsing. Defaults to False.

    Returns:
        bool: True if the value can be parsed as a datetime, False otherwise.

    """
    try:
        parse(element, fuzzy=fuzzy)
        return True
    except ValueError:
        return False


def is_integer(element):
    """Check if a value can be converted to an integer.

    Args:
        element (any): The value to check.

    Returns:
        bool: True if the value can be converted to an integer, False otherwise.

    """
    try:
        return float(element).is_integer()
    except ValueError:
        return False


def reformat_json(yaml):
    """Reformat a JSON object.

    Args:
        yaml (dict): The JSON object to reformat.

    Returns:
        dict: The reformatted JSON object.

    """
    result = {}
    for key, value in yaml.items():
        if value in ["true", "false"]:
            result[key] = str2bool(value)
        elif isinstance(value, dict):
            result[key] = value
        elif not isinstance(value, bool) and is_float(value):
            result[key] = float(value)
        else:
            result[key] = value
    return result


def truncate(f, n=2):
    """Truncate a float number to a specified number of decimal places.

    Args:
        f (float): The float number to truncate.
        n (int, optional): The number of decimal places to keep. Defaults to 2.

    Returns:
        float: The truncated float number.

    """
    return floor(f * 10**n) / 10**n


def title(message):
    """Print a title message.

    Args:
        message (str or list): The message or list of messages to print as a title.

    """
    separator()
    if isinstance(message, list):
        for msg in message:
            logging.info(f"{msg.upper()}")
    else:
        logging.info(f"{message.upper()}")
    separator()


def title_warning(message):
    """Print a warning message with a title format.

    Args:
        message (str): The warning message to print.

    """
    separator_warning()
    logging.warning(f" {message.upper()}")
    separator_warning()


def separator():
    """Print a separator line."""
    logging.info(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ ❖ ◦ "
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def separator_warning():
    """Print a warning separator line."""
    logging.warning(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ▲ "
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def export_finish():
    """Finish the export process."""
    logging.info(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ TERMINE ◦ "
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def log_usage_point_id(usage_point_id):
    """Log the usage point ID.

    Args:
        usage_point_id (str): The usage point ID to log.
    """
    text = f"Point de livraison : {usage_point_id}"
    separator()
    logging.info(f'{decor("barcode1")}{text: ^93}{decor("barcode1", reverse=True)}')
    separator()


def finish():
    """Finish the import process."""
    separator()
    for line in text2art("Import Finish!!!").splitlines():
        logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
    separator()


def get_version():
    """Return the version of the module."""
    return VERSION


def logo(version):
    """Print the logo of MyElectricalData with the version number.

    Args:
        version (str): The version number of MyElectricalData.

    """
    art = text2art("MyElectricalData")
    separator()
    for line in art.splitlines():
        logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
    separator()
    version = f"VERSION : {version}"
    logging.info(f'{decor("barcode1")}{version: ^93}{decor("barcode1", reverse=True)}')
    separator()


def check_format(value):
    """Check the format of a value and convert it if necessary.

    Args:
        value (any): The value to check and convert.

    Returns:
        any: The checked and converted value.

    """
    if is_bool(value):
        new_value = str2bool(value)
    elif value is None or value == "None" or not value:
        new_value = None
    elif isinstance(value, int):
        new_value = int(value)
    elif is_float(value):
        new_value = float(value)
    elif is_datetime(value):
        new_value = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=pytz.utc)
    else:
        new_value = str(value)
    return new_value


def is_between(time, time_range):
    """Check if a given time is between a specified time range.

    Args:
        time (datetime): The time to check.
        time_range (tuple): The time range represented by a tuple of two datetime objects.

    Returns:
        bool: True if the time is between the time range, False otherwise.
    """
    time = time.replace(":", "")
    start = time_range[0].replace(":", "")
    end = time_range[1].replace(":", "")
    if end < start:
        return time >= start or time < end
    return start <= time < end
