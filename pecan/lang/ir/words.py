#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ir.arith import Add, Less
from pecan.lang.ir.base import IREvaluation, IRPredicate
from pecan.lang.ir.prog import Call

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.base import IRExpression
    from pecan.lang.ir.prog import VarRef

class IndexRange(IRPredicate):
    def __init__(self, var_name : str, start : IRExpression, end : IRExpression):
        super().__init__()
        self.var_name : str = var_name
        self.start : IRExpression = start
        self.end : IRExpression = end

    def bounds_check(self, idx_var : VarRef) -> Less:
        return Less(Add(self.start, idx_var).with_type(self.start.get_type()), self.end)

    def index_expr(self, idx_var : VarRef) -> Call:
        return Call(self.var_name, [Add(self.start, idx_var).with_type(self.start.get_type())])

    def transform(self, transformer : IRTransformer) -> IndexRange:
        return transformer.transform_IndexRange(self)

    def __str__(self) -> str:
        return '{}[{}..{}]'.format(self.var_name, self.start, self.end)

class EqualsCompareRange(IRPredicate):
    def __init__(self, is_equals : bool, index_a : IndexRange, index_b : IndexRange):
        super().__init__()
        self.is_equals : bool = is_equals
        self.index_a : IndexRange = index_a
        self.index_b : IndexRange = index_b

    def transform(self, transformer : IRTransformer) -> EqualsCompareRange:
        return transformer.transform_EqualsCompareRange(self)

    def __str__(self) -> str:
        if self.is_equals:
            return '{} = {}'.format(self.index_a, self.index_b)
        else:
            return '{} ≠ {}'.format(self.index_a, self.index_b)

