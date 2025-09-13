import logging
import os
from app.middlewares.contextmiddleware import get_request_id
from app.utilities.constants import Constants


def get_logger(
    name, level=logging.INFO, file_name=Constants.fetch_constant("base_log_file_path")
):
    """logger method to get logger from
    author: Rajesh
    Args:
        name (_type_): _description_
    Returns:
        _type_: _description_
    """
    log_format = "%(levelname)s : %(asctime)-5s %(filename)s:%(lineno)d %(funcName)-5s --> %(message)s"
    if not os.path.exists(file_name):
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
    logging.basicConfig(
        format=log_format,
        filename=file_name,
        filemode="a",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
    )
    logger = logging.getLogger(name)
    return logger


class BIALogger(logging.LoggerAdapter):
    """Base class with logger enabled with adding a uniqueid for each request
    author: andy
    Args:
        logging ([type]): [description]
    """

    def process(self, msg, kwargs):
        if get_request_id() is not None:
            return "[%s] %s" % (get_request_id(), msg), kwargs
        else:
            return "%s" % (msg), kwargs
