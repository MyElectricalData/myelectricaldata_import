"""Generic utils."""

import decimal
import json
import logging
import re
import shutil
import sys
from datetime import datetime, timedelta
from math import floor
from os import getenv
from pathlib import Path
from typing import ClassVar, Union

import pytz
import yaml
from art import decor, text2art
from dateutil.parser import parse
from mergedeep import Strategy, merge
from ruamel.yaml import YAML
from ruamel.yaml import comments as com

from __version__ import VERSION
from const import URL_CONFIG_FILE


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


def reformat_json(entry):
    """Reformat a JSON object.

    Args:
        entry (dict): The JSON object to reformat.

    Returns:
        dict: The reformatted JSON object.

    """
    result = {}
    for key, value in entry.items():
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


def convert_kw(value):
    """Convert a value from kilowatts to watts.

    Args:
        value (float): The value in kilowatts.

    Returns:
        float: The value in watts.
    """
    return truncate(value / 1000, 2)


def convert_kw_to_euro(value, price):
    """Convert a value from kilowatts to euros.

    Args:
        value (float): The value in kilowatts.
        price (float): The price per kilowatt-hour.

    Returns:
        float: The value in euros.
    """
    if isinstance(price, str):
        price = float(price.replace(",", "."))
    return round(value / 1000 * price, 1)


def convert_price(price):
    """Convert a price from string to float.

    Args:
        price (str): The price as a string.

    Returns:
        float: The price as a float.
    """
    if isinstance(price, str):
        price = price.replace(",", ".")
    return float(price)


def force_round(x, n):
    """Round a number to a specified number of decimal places.

    Args:
        x (float): The number to be rounded.
        n (int): The number of decimal places to round to.

    Returns:
        float: The rounded number.
    """
    d = decimal.Decimal(repr(x))
    targetdigit = decimal.Decimal("1e%d" % -n)
    chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
    return float(chopped)


def object_to_dict(obj):
    """Convert an object to a dictionary.

    Args:
        obj (object): The object to convert.

    Returns:
        dict: The dictionary representation of the object.
    """
    return json.loads(json.dumps(obj, default=lambda o: getattr(o, "__dict__", str(o))))


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


def title_critical(message):
    """Print a critical message with a title format.

    Args:
        message (str): The warning message to print.

    """
    separator_critical()
    logging.critical(f" {message.upper()}")
    separator_critical()


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


def separator_critical():
    """Print a critical separator line."""
    logging.critical(
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
    logging.info(f"{decor('barcode1')}{text: ^93}{decor('barcode1', reverse=True)}")
    separator()


def finish():
    """Finish the import process."""
    separator()
    for line in text2art("Import Finish!!!").splitlines():
        logging.info(f"{decor('barcode1')}{line: ^93}{decor('barcode1', reverse=True)}")
    separator()


def get_version():
    """Return the version of the module."""
    return VERSION


def barcode_message(message):
    """Barcode message."""
    art = text2art(message)
    for line in art.splitlines():
        logging.info(f"{decor('barcode1')}{line: ^93}{decor('barcode1', reverse=True)}")


def logo(version):
    """Print the logo of MyElectricalData with the version number.

    Args:
        version (str): The version number of MyElectricalData.

    """
    art = text2art("MyElectricalData")
    separator()
    for line in art.splitlines():
        logging.info(f"{decor('barcode1')}{line: ^93}{decor('barcode1', reverse=True)}")
    separator()
    version = f"VERSION : {version}"
    logging.info(f"{decor('barcode1')}{version: ^93}{decor('barcode1', reverse=True)}")
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


def chunks_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def is_json(myjson):
    """Check if a string is a valid JSON object."""
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


class ConfigOutput:
    """Return object."""

    application_path: str = None
    application_path_data: str = None
    application_path_log: str = None
    config_file: str = None
    config: ClassVar[dict] = {}


def load_config() -> ConfigOutput:
    """Load config.yaml file."""
    output = ConfigOutput()
    output.application_path = getenv("APPLICATION_PATH", "/app")
    error = False
    if not Path(output.application_path).is_dir():
        error = True
        logging.error(
            (
                "\n\nLe dossier contenant les sources n'existe pas.\n"
                " Variable d'environnement : APPLICATION_PATH\n => %s\n"
            ),
            getenv("APPLICATION_PATH"),
        )
    output.application_path_data = getenv("APPLICATION_PATH_DATA", "/data")
    if not Path(output.application_path_data).is_dir():
        error = True
        logging.error(
            (
                "\n\nLe dossier contenant les données n'existe pas.\n"
                " Variable d'environnement : APPLICATION_PATH_DATA\n => %s\n"
            ),
            getenv("APPLICATION_PATH_DATA"),
        )
    output.application_path_log = getenv("APPLICATION_PATH_LOG", "/log")
    if not Path(output.application_path_log).is_dir():
        error = True
        logging.error(
            (
                "\n\nLe dossier contenant les logs n'existe pas.\n"
                " Variable d'environnement : APPLICATION_PATH_LOG\n => %s\n"
            ),
            getenv("APPLICATION_PATH_LOG"),
        )
    if error:
        sys.exit(1)
    output.config_file = f"{output.application_path_data}/config.yaml"
    if not Path(output.config_file).exists() or Path(output.config_file).stat().st_size == 0:
        shutil.copyfile(f"{output.application_path}/templates/config.example.yaml", output.config_file)
    try:
        # Check Usage Point Id single quote
        config_path = Path(output.config_file)
        content_new = re.sub(r"  ([0-9]*)\:", r"  '\1':", config_path.read_text(encoding="UTF-8"), flags=re.M)
        config_path.write_text(content_new, encoding="UTF-8")
        with Path(output.config_file).open(encoding="utf-8") as file:
            output.config = yaml.safe_load(file)
    except yaml.YAMLError:
        logging.critical(
            f"""
    Impossible de charger le fichier de configuration.

    Vous pouvez récupérer un exemple de configuration ici:
    {URL_CONFIG_FILE}
"""
        )
        sys.exit(1)
    return output


def edit_config(data, file=None, comments=None, wipe=False):  # noqa: C901
    """Edit a value in a YAML file."""
    if file is None:
        file = load_config().config_file
    config_path = Path(file)
    yaml_obj = YAML()
    yaml_obj.indent(mapping=2, sequence=4, offset=2)

    code = yaml_obj.load(config_path.read_text(encoding="UTF-8")) if not wipe else {}
    if code is None:
        code = {}
    # CLEAN OLD CONFIGURATION
    if "wipe_influxdb" in code:
        del code["wipe_influxdb"]
    if "debug" in code:
        del code["debug"]
    if "log2file" in code:
        del code["log2file"]
    if "port" in code:
        del code["port"]
    if "ssl" in code:
        del code["ssl"]
    new_config = merge(code, data, strategy=Strategy.ADDITIVE)
    new_config = dict(sorted(new_config.items()))
    if comments is not None:
        comments_obj = com.CommentedMap()
        for key, value in comments.items():
            comments_obj.yaml_add_eol_comment(value, key, column=1)
            new_config = merge(comments_obj, code, strategy=Strategy.ADDITIVE)
    for key, value in new_config.items():
        currant_value = value
        if isinstance(currant_value, list):
            currant_value = list(set(currant_value))
            new_config[key] = currant_value
        if isinstance(currant_value, Union[dict, list]):
            for sub_key, sub_value in currant_value.items():
                current_sub_value = sub_value
                if isinstance(current_sub_value, list):
                    current_sub_value = list(set(current_sub_value))
                    new_config[key][sub_key] = current_sub_value

    with config_path.open("w", encoding="UTF-8") as f:
        yaml_obj.dump(new_config, f)
