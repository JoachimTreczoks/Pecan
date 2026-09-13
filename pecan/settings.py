#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import os
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal, Callable
    from pecan.lang.ir.prog import Program

class Settings:
    """Static settings holder class, to interface with the program settings from anywhere in the code"""

    """Regular settings. Can be fully read and written to via getters and setters from outside"""
    _debug_level : int = 0
    _quiet : bool = False
    _opt_level : int = 1
    _load_stdlib : bool = True
    _history_file : str = 'pecan_history'
    _simplification_level : int = 1
    _should_use_heuristics : bool = False
    _postprocessing_preference : Literal['Small', 'Deterministic'] = 'Small'
    _postprocessing_force_sbacc : bool = False
    _only_min_opt : bool = False
    _extract_implications : bool = False
    _write_statistics : bool = False
    _output_hoa : str | None = None
    _output_json : bool = False
    _show_progress : bool = True

    """Internal settings. Cannot be written to from outside"""
    _output : str = ''
    _stdlib_prog : Program | None = None
    _pecan_path_var : str = 'PECAN_PATH'

    @staticmethod
    def get_output() -> str:
        return Settings._output
    
    @staticmethod
    def get_pecan_path() -> list[str]:
        if Settings._pecan_path_var in os.environ:
            return os.getenv(Settings._pecan_path_var).split(os.pathsep)
        else:
            return []

    @staticmethod
    def include_stdlib(prog : Program, loader : Callable[[str, tuple, dict], Program], args : tuple, kwargs : dict):
        if Settings.should_load_stdlib():
            orig_debug_level = Settings.get_debug_level()
            before = Settings.should_load_stdlib()
            before_quiet = Settings.is_quiet()
            try:
                # Don't want to load stdlib while loading stdlib
                Settings.set_load_stdlib(False)
                Settings.set_quiet(True)
                Settings.set_debug_level(orig_debug_level - 1)

                if Settings._stdlib_prog is None:
                    Settings._stdlib_prog = loader(prog.locate_file('std.pn'), *args, **kwargs)
                    Settings._stdlib_prog.evaluate_prog()

                prog.include(Settings._stdlib_prog)
            finally:
                Settings.set_load_stdlib(before)
                Settings.set_quiet(before_quiet)
                Settings.set_debug_level(orig_debug_level)

        return prog
    
    @staticmethod
    def print(s : str) -> None:
        if Settings.get_output_json():
            Settings._output += s + "\n"
        else:
            print(s)
        return None

    @staticmethod
    def set_output_json(output_json : bool) -> None:
        Settings._output_json = output_json
        return None

    @staticmethod
    def get_output_json() -> bool:
        return Settings._output_json

    @staticmethod
    def set_show_progress(show_progress : bool) -> None:
        Settings._show_progress = show_progress
        return None

    @staticmethod
    def get_show_progress() -> bool:
        return Settings._show_progress and not Settings._quiet

    @staticmethod
    def set_write_statistics(write_statistics : bool) -> None:
        Settings._write_statistics = write_statistics
        return None

    @staticmethod
    def should_write_statistics() -> bool:
        return Settings._write_statistics

    @staticmethod
    def set_extract_implications(b : bool) -> None:
        Settings._extract_implications = b
        return None

    @staticmethod
    def get_extract_implications() -> bool:
        return Settings._extract_implications

    @staticmethod
    def set_min_opt(min_opt : bool) -> None:
        Settings._only_min_opt = min_opt
        return None

    @staticmethod
    def min_opt() -> bool:
        return Settings._only_min_opt

    @staticmethod
    def set_simplification_level(new_level : int) -> None:
        Settings._simplification_level = new_level
        return None

    @staticmethod
    def get_simplification_level() -> int:
        return Settings._simplification_level

    @staticmethod
    def set_history_file(filename : str) -> None:
        Settings._history_file = filename
        return None

    @staticmethod
    def get_history_file() -> Path:
        return Path.home() / Settings._history_file

    @staticmethod
    def set_debug_level(level : int) -> None:
        Settings._debug_level = max(0, level)
        return None

    @staticmethod
    def get_debug_level() -> int:
        return Settings._debug_level

    @staticmethod
    def set_quiet(val : bool) -> None:
        Settings._quiet = val
        return None

    @staticmethod
    def is_quiet() -> bool:
        return Settings._quiet

    @staticmethod
    def set_opt_level(level : int) -> None:
        assert level >= 0
        Settings._opt_level = level
        return None

    @staticmethod
    def get_opt_level() -> int:
        return Settings._opt_level

    @staticmethod
    def opt_enabled() -> bool:
        return Settings._opt_level > 0

    @staticmethod
    def set_use_heuristics(use_heuristics : bool) -> None:
        Settings._should_use_heuristics = use_heuristics
        return None

    @staticmethod
    def use_heuristics() -> bool:
        return Settings._should_use_heuristics

    @staticmethod
    def set_load_stdlib(val : bool) -> None:
        Settings._load_stdlib = val
        return None

    @staticmethod
    def should_load_stdlib() -> bool:
        return Settings._load_stdlib

    @staticmethod
    def set_output_hoa(hoa_file : str) -> None:
        Settings._output_hoa = hoa_file
        return None

    @staticmethod
    def get_output_hoa() -> str | None:
        return Settings._output_hoa

    @staticmethod
    def set_postprocessing_preference(val : Literal['Small', 'Deterministic']) -> None:
        Settings._postprocessing_preference = val
        return None

    @staticmethod
    def get_postprocessing_preference() -> Literal['Small', 'Deterministic']:
        return Settings._postprocessing_preference

    @staticmethod
    def set_postprocessing_force_sbacc(val : bool) -> None:
        Settings._postprocessing_force_sbacc = val
        return None

    @staticmethod
    def get_postprocessing_force_sbacc() -> bool:
        return Settings._postprocessing_force_sbacc
