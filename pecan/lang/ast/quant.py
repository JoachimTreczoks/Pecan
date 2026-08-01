#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from functools import reduce

from pecan.lang.ast.bool import BoolConst, Conjunction, Implies
from pecan.lang.ast.base import Predicate
from pecan.lang.ast.prog import VarRef
from pecan.lang.ast.prog import Call
from pecan.utility import unzip

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer

def to_ref(var_ref : str | VarRef) -> VarRef:
    if isinstance(var_ref, VarRef):
        return var_ref
    else:
        return VarRef(var_ref)

def extract_var_cond(var_pred) -> tuple[VarRef, Call | None]:
    if isinstance(var_pred, Call):
        return to_ref(var_pred.args[-1]), var_pred
    else:
        return to_ref(var_pred), None

class Forall(Predicate):
    def __init__(self, var_preds, pred):
        super().__init__()
        self.var_preds = var_preds
        self.vars, self.conds = unzip(map(extract_var_cond, var_preds))
        self.pred = pred

    def transform(self, transformer : AstTransformer) -> Forall:
        return transformer.transform_Forall(self)

    def build_cond(self):
        return reduce(Conjunction, [c for c in self.conds if c is not None], BoolConst(True))

    def __str__(self) -> str:
        return '(∀{}. {})'.format(', '.join(map(str, self.vars)), Implies(self.build_cond(), self.pred))

class Exists(Predicate):
    def __init__(self, var_preds, pred):
        super().__init__()
        self.var_preds = var_preds
        self.vars, self.conds = unzip(map(extract_var_cond, var_preds))
        self.pred = pred

    def transform(self, transformer : AstTransformer) -> Exists:
        return transformer.transform_Exists(self)

    def build_cond(self):
        return reduce(Conjunction, [c for c in self.conds if c is not None], BoolConst(True))

    def __str__(self) -> str:
        return '(∃{}. {})'.format(', '.join(map(str, self.vars)), Conjunction(self.build_cond(), self.pred))

