"""This module contains dependencies for the application."""
import datetime
import logging
from math import floor
from os import environ, getenv

from art import decor, text2art

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
        yield start_date + datetime.timedelta(n)


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
    if type(v) != bool:
        return v and v.lower() in ("yes", "true", "t", "1")
    else:
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
        elif type(value) == dict:
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
    if type(message) is list:
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
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ ❖ ◦ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def separator_warning():
    """Print a warning separator line."""
    logging.warning(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ▲ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def export_finish():
    """Finish the export process."""
    logging.info(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ TERMINE ◦ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
    Art = text2art("MyElectricalData")
    separator()
    for line in Art.splitlines():
        logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
    separator()
    version = f"VERSION : {version}"
    logging.info(f'{decor("barcode1")}{version: ^93}{decor("barcode1", reverse=True)}')
    separator()

def chunks_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
