#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

# This module provides an infrastructure for configuring Pecan
# All uses of various config options like debug mode, quiet mode, etc. are managed from here

import os

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal, Callable
    from pecan.lang.ir.prog import Program

class Settings:
    def __init__(self):
        self.debug_level : int = 0
        self.quiet : bool = False
        self.opt_level : int = 1
        self.load_stdlib : bool = True
        self.pecan_path_var : str = 'PECAN_PATH'
        self.history_file : str = 'pecan_history'
        self.simplification_level : int = 1
        self.should_use_heuristics : bool = False
        self.postprocessing_preference : Literal['Small', 'Deterministic'] = 'Small'
        self.postprocessing_force_sbacc : bool = False
        self.only_min_opt : bool = False
        self.extract_implications : bool = False
        self.write_statistics : bool = False
        self.output_hoa : str | None = None
        self.output_json : bool = False
        self.show_progress : bool = True

        self.output : str = ''

        self.stdlib_prog : Program | None = None

    def get_output(self) -> str:
        return self.output

    def set_output_json(self, output_json : bool) -> Settings:
        self.output_json = output_json
        return self

    def print(self, s : str) -> Settings:
        if self.get_output_json():
            self.output += s + "\n"
        else:
            print(s)
        return self

    def set_show_progress(self, show_progress : bool) -> Settings:
        self.show_progress = show_progress
        return self

    def get_show_progress(self) -> bool:
        return self.show_progress and not self.quiet

    def get_output_json(self) -> bool:
        return self.output_json

    def should_write_statistics(self) -> bool:
        return self.write_statistics

    def set_write_statistics(self, write_statistics : bool) -> Settings:
        self.write_statistics = write_statistics
        return self

    def get_extract_implications(self) -> bool:
        return self.extract_implications

    def set_extract_implications(self, b : bool) -> Settings:
        self.extract_implications = b
        return self

    def min_opt(self) -> bool:
        return self.only_min_opt

    def set_min_opt(self, min_opt : bool) -> Settings:
        self.only_min_opt = min_opt
        return self

    def get_simplification_level(self) -> int:
        return self.simplification_level

    def set_simplification_level(self, new_level : int) -> Settings:
        self.simplification_level = new_level
        return self

    def get_history_file(self) -> Path:
        return Path.home() / self.history_file

    def set_history_file(self, filename : str) -> Settings:
        self.history_file = filename
        return self

    def get_pecan_path(self) -> list[str]:
        if self.pecan_path_var in os.environ:
            return os.getenv(self.pecan_path_var).split(os.pathsep)
        else:
            return []

    def set_debug_level(self, level : int) -> Settings:
        self.debug_level = max(0, level)
        return self

    def get_debug_level(self) -> int:
        return self.debug_level

    def set_quiet(self, val : bool) -> Settings:
        self.quiet = val
        return self

    def is_quiet(self) -> bool:
        return self.quiet

    def set_opt_level(self, level : int) -> Settings:
        assert level >= 0
        self.opt_level = level
        return self

    def get_opt_level(self) -> int:
        return self.opt_level

    def opt_enabled(self) -> bool:
        return self.opt_level > 0

    def set_use_heuristics(self, use_heuristics : bool) -> Settings:
        self.should_use_heuristics = use_heuristics
        return self

    def use_heuristics(self) -> bool:
        return self.should_use_heuristics

    def set_load_stdlib(self, val : bool) -> Settings:
        self.load_stdlib = val
        return self

    def should_load_stdlib(self) -> bool:
        return self.load_stdlib

    def set_output_hoa(self, hoa_file : str) -> Settings:
        self.output_hoa = hoa_file
        return self

    def get_output_hoa(self) -> str | None:
        return self.output_hoa

    def include_stdlib(self, prog : Program, loader : Callable[[str, tuple, dict], Program], args : tuple, kwargs : dict):
        if self.should_load_stdlib():
            orig_debug_level = self.get_debug_level()
            before = self.should_load_stdlib()
            before_quiet = self.is_quiet()
            try:
                # Don't want to load stdlib while loading stdlib
                self.set_load_stdlib(False)
                self.set_quiet(True)
                self.set_debug_level(orig_debug_level - 1)

                if self.stdlib_prog is None:
                    self.stdlib_prog = loader(prog.locate_file('std.pn'), *args, **kwargs)
                    self.stdlib_prog.evaluate_prog()

                prog.include(self.stdlib_prog)
            finally:
                self.set_load_stdlib(before)
                self.set_quiet(before_quiet)
                self.set_debug_level(orig_debug_level)

        return prog

    def set_postprocessing_preference(self, val : Literal['Small', 'Deterministic']) -> Settings:
        self.postprocessing_preference = val
        return self

    def get_postprocessing_preference(self) -> Literal['Small', 'Deterministic']:
        return self.postprocessing_preference

    def set_postprocessing_force_sbacc(self, val : bool) -> Settings:
        self.postprocessing_force_sbacc = val
        return self

    def get_postprocessing_force_sbacc(self) -> bool:
        return self.postprocessing_force_sbacc

settings = Settings()

