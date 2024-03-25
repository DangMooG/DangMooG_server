import os
import logging
from logging.config import fileConfig


log_option = os.environ.get("LOG_OPTION", "root")
if log_option not in ["root", "logstashOnly", "consoleOnly"]:
    raise Exception("logger_name(" + log_option + ") does not exist")

fileConfig('logging.conf', disable_existing_loggers=True)


class LoggerSetup:
    def __init__(self, name) -> None:
        self.logger = logging.getLogger(name)