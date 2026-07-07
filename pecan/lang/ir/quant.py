#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from functools import reduce

from pecan.lang.ir.base import IRPredicate
from pecan.lang.ir.bool import Conjunction

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.prog import Program, VarRef, Call
    from pecan.lang.ir.base import IREvaluation

class Exists(IRPredicate):
    def __init__(self, var_refs : list[VarRef], conds : list[Call], pred : IRPredicate):
        super().__init__()
        self.var_refs : list[VarRef] = var_refs
        self.conds : list[Call] = conds
        self.pred : IRPredicate = pred

    def evaluate_node(self, prog : Program) -> IREvaluation:
        for v, cond in zip(self.var_refs, self.conds):
            if cond is not None:
                prog.restrict(v.var_name, cond)

        all_constraints = self.get_prog_constraints(prog)
        aut = self.with_cond(all_constraints + self.conds, self.pred).evaluate(prog)
        res = aut.project(self.var_refs, prog.get_var_map())

        for v, cond in zip(self.var_refs, self.conds):
            if cond is not None:
                prog.forget(v.var_name)

        return res

    def get_prog_constraints(self, prog : Program) -> list[Call]:
        all_constraints = []

        for v in self.var_refs:
            all_constraints.extend(prog.get_restrictions(v.var_name))

        return all_constraints

    def with_cond(self, conds : list[Call], pred : IRPredicate) -> IRPredicate:
        cond = self.build_cond(set(conds))
        if cond is None:
            return pred
        else:
            return Conjunction(cond, pred)

    def transform(self, transformer : IRTransformer) -> Exists:
        return transformer.transform_Exists(self)

    def build_cond(self, conds : set[IRPredicate]) -> IRPredicate | None:
        filtered_cs = [c for c in conds if c is not None]

        if len(filtered_cs) == 0:
            return None
        else:
            return reduce(Conjunction, [c for c in conds if c is not None])

    def __str__(self) -> str:
        return '(∃{}. {})'.format(self.var_refs, self.with_cond(self.conds, self.pred))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var_refs == other.var_refs and self.conds == other.conds and self.pred == other.pred

    def __hash__(self) -> int:
        return hash((tuple(self.var_refs), tuple(self.conds), self.pred))

