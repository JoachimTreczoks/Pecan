
from pecan.settings import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any

class Logger:

    @staticmethod
    def log(level : int, msg : str):
        settings.log(level, lambda: msg)

    @staticmethod
    def info(msg : str):
        Logger.log(-1, '[INFO] {}'.format(msg))

    @staticmethod
    def debug(level : int, msg : str):
        Logger.log(level, '[DEBUG] {}'.format(msg))

    @staticmethod
    def warn(msg : str):
        Logger.log(-1, '[WARN] {}'.format(msg))

    @staticmethod
    def typecheck(name : str, var : Any):
        Logger.log(0, '[TYPE CHECK] type({}) = {}'.format(name, type(var)))
