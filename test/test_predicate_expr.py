#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan import program
from pecan.settings import Settings

def run_file(filename):
    orig_quiet = Settings.is_quiet()
    Settings.set_quiet(True)

    prog = program.load(filename)
    assert prog.evaluate_prog().result.succeeded()

    Settings.set_quiet(orig_quiet)

def test_min_function():
    run_file('examples/test_min_function.pn')

def test_max_function():
    run_file('examples/test_max_function.pn')

def test_inf_function():
    run_file('examples/test_inf_function.pn')

def test_sup_function():
    run_file('examples/test_sup_function.pn')

def test_div():
    run_file('examples/test_div.pn')
