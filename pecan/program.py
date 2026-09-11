#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import os

from pecan.lang.parser import pecan_parser
from pecan.lang.ast_to_ir import ASTToIR
from pecan.lang.optimizer.optimizer import UntypedOptimizer

from pecan.settings import Settings
from pecan.logger import Logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from pecan.lang.ast.prog import Program as ASTProgram
    from pecan.lang.ir.prog import Program

def make_search_paths(filename : str | None=None) -> list[str]:
    own_path = os.path.dirname(os.path.realpath(__file__))
    std_library_path = os.path.join(own_path, '..', 'library')
    automata_library_path = os.path.join(own_path, '..', 'library', 'automata')

    # Always include the current directory and the standard library folder
    search_paths = ['.', std_library_path, automata_library_path]

    # If we're creating a search path for some file (which is almost always the case), then include the base directory of that file as well
    if filename is not None:
        search_paths.append(os.path.dirname(filename))

    search_paths.extend(Settings.get_pecan_path())

    return search_paths

def load(pecan_file : str, *args : tuple, **kwargs : dict) -> Program:
    with open(pecan_file, 'r', encoding='utf-8') as f:
        kwargs['filename'] = pecan_file
        return from_source(f.read(), *args, **kwargs)

def from_source(source_code : str, *args : tuple, **kwargs : dict) -> Program:
    astprog : ASTProgram = pecan_parser.parse(source_code)

    Logger.log('Parsed program:', 4)
    Logger.log(str(astprog), 4)

    astprog.search_paths = make_search_paths(filename=kwargs.get('filename', None))
    astprog.loader = load

    if Settings.get_extract_implications():
        astprog.extract_implications()

    prog : Program = ASTToIR().transform(astprog)

    Logger.log('Search path: {}'.format(prog.search_paths), 0)

    # Load the standard library
    prog = Settings.include_stdlib(prog, load, args, kwargs)

    if Settings.opt_enabled():
        prog = UntypedOptimizer(prog).optimize()

        Logger.log('(Untyped) Optimized program:', 1)
        Logger.log(str(prog), 1)

    return prog

