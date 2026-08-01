
from pecan.settings import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any

class Logger:

    @staticmethod
    def log(msg : str, level : int = -1, respect_quiet : bool = False):
        if settings.get_debug_level() > level and (settings.is_quiet() or not respect_quiet):
            settings.print(msg)

    @staticmethod
    def info(msg : str, level : int = -1, respect_quiet : bool = False):
        Logger.log('[INFO] {}'.format(msg), level, respect_quiet)

    @staticmethod
    def debug(msg : str, level : int = 0, respect_quiet : bool = False):
        Logger.log('[DEBUG] {}'.format(msg), level, respect_quiet)

    @staticmethod
    def warn(msg : str, level : int = -1, respect_quiet : bool = False):
        Logger.log('[WARN] {}'.format(msg), level, respect_quiet)

    @staticmethod
    def error(msg : str, level : int = -1, respect_quiet : bool = False):
        Logger.log('[ERROR] {}'.format(msg), level, respect_quiet)

    @staticmethod
    def typecheck(name : str, var : Any, level : int = 0, respect_quiet : bool = False):
        Logger.log('[TYPE CHECK] type({}) = {}'.format(name, type(var)), level, respect_quiet)
