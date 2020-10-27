import logging
import getpass
import os
from logging.handlers import RotatingFileHandler

import enum


class Level(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Log(object):
    def __init__(self, title="", path="", level=Level.DEBUG.value):
        user = getpass.getuser()
        self.user_log = logging.getLogger(user)
        self.user_log.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s @ %(name)s   [%(levelname)-7s] %(message)s')

        if not os.path.isdir(path):
            os.mkdir(path)
        folder_path = os.path.join(path, "Logging")
        path = os.path.join(folder_path, "UserLog.log")
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)

        rotating_handler = RotatingFileHandler(path, maxBytes=20000000, backupCount=10, encoding='utf-8')
        rotating_handler.setLevel(level)
        rotating_handler.setFormatter(formatter)
        self.user_log.addHandler(rotating_handler)

        console_handle = logging.StreamHandler()
        console_handle.setLevel(level)
        console_handle.setFormatter(formatter)
        self.user_log.addHandler(console_handle)
        # self.debug("----------"*5 + title + "----------"*5)

    def debug(self, msg):
        self.user_log.debug(msg)

    def info(self, msg):
        self.user_log.info(msg)

    def warning(self, msg):
        self.user_log.warning(msg)

    def error(self, msg):
        self.user_log.error(msg,exc_info=1)

    def critical(self, msg):
        self.user_log.critical(msg)

    def log(self, level, msg):
        self.user_log.log(level, msg)

    def set_level(self, level):
        self.user_log.setLevel(level)

    def disable(self):
        self.user_log.disabled(50)

