#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import copy
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from _collections_abc import dict_items
    from typing import Callable

# From: https://stackoverflow.com/a/6222692/1498618
def touch(filename : str) -> None:
    try:
        os.utime(filename, None)
    except OSError:
        with open(filename, 'a'):
            pass

def unzip(xs : map) -> tuple[list, list]:
    lefts = []
    rights = []

    for l, r in xs:
        lefts.append(l)
        rights.append(r)

    return lefts, rights

class VarMap:
    def __init__(self, var_reps : dict[str, list[str]] | None=None):
        self.var_reps : dict = var_reps or {}

    def clone(self) -> VarMap:
        return VarMap(copy.deepcopy(self.var_reps))

    def __contains__(self, item : str) -> bool:
        return item in self.var_reps

    def __getitem__(self, item : str) -> list[str]:
        return self.var_reps[item]

    def __setitem__(self, item : str, value : list[str]) -> None:
        self.var_reps[item] = value

    def items(self) -> dict_items[str, list[str]]:
        return self.var_reps.items()

    def pop(self, key : str) -> list[str]:
        return self.var_reps.pop(key)

    def merge_with(self, other : VarMap) -> tuple[VarMap, dict]:
        merged_var_map = self.clone()

        # The substitutions that need to be made to the representation values for this merge to be valid
        subs = {}

        for var, reps in other.var_reps.items():
            if var in merged_var_map:
                merged_reps = merged_var_map[var]

                if len(merged_reps) != len(reps):
                    raise Exception('Cannot merge {}: representations differ in length ({}, {})'.format(var, merged_reps, reps))

                for a, b in zip(merged_reps, reps):
                    subs[b] = a
            else:
                merged_var_map[var] = reps

        return merged_var_map, subs

    def get_or_gen(self, var_name : str, gen_func : Callable[[], str], n_reps : int) -> list[str]:
        if var_name not in self:
            self[var_name] = [ gen_func() for _ in range(n_reps) ]

        return self[var_name]

    def __repr__(self) -> str:
        return 'VarMap({})'.format(self.var_reps)

    def update(self, other : VarMap) -> None:
        self.var_reps.update(other.var_reps)

    def to_str(self) -> str:
        return repr(self.var_reps)

