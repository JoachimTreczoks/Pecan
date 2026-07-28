#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast.arith import IntConst
from pecan.lang.ast.base import Predicate
from pecan.lang.ast.bool import BoolConst

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer
    from pecan.lang.ast.base import Expression

class Index(Predicate):
    def __init__(self, var_name : str, index_expr : Expression):
        super().__init__()
        self.var_name : str = var_name
        self.index_expr : Expression = index_expr

    def transform(self, transformer : AstTransformer) -> Index:
        return transformer.transform_Index(self)

    def __str__(self) -> str:
        return '{}[{}]'.format(self.var_name, self.index_expr)

class IndexRange(Predicate):
    def __init__(self, var_name : str, start : Expression, end : Expression):
        super().__init__()
        self.var_name : str = var_name
        self.start : Expression = start
        self.end : Expression = end

    def transform(self, transformer : AstTransformer) -> IndexRange:
        return transformer.transform_IndexRange(self)

    def __str__(self) -> str:
        return '{}[{}..{}]'.format(self.var_name, self.start, self.end)

class EqualsCompareIndex(Predicate):
    def __init__(self, is_equals : bool, index_a : Index, index_b : IntConst | Index):
        super().__init__()
        self.is_equals : bool = is_equals
        self.index_a : Index = index_a

        if isinstance(index_b, IntConst):
            if index_b.val == 0:
                self.index_b : BoolConst | Index = BoolConst(False)
            elif index_b.val == 1:
                self.index_b : BoolConst | Index = BoolConst(True)
            else:
                # TODO: Remove this restriction
                raise ValueError('Automatic words can only be binary (i.e., 0 or 1), {} is not allowed (in "{} = {}")'.format(index_b.val, index_a, index_b))
        elif isinstance(index_b, Index):
            self.index_b : BoolConst | Index = index_b
        else:
            raise IndexError('Unexpected index expression on RHS: {} = {}'.format(index_a, index_b))

    def transform(self, transformer : AstTransformer) -> EqualsCompareIndex:
        return transformer.transform_EqualsCompareIndex(self)

    def format(self, x : BoolConst | Index) -> IntConst | str:
        if isinstance(x, BoolConst):
            return IntConst(1 if x.bool_val else 0)
        else:
            return str(x)

    def __str__(self) -> str:
        if self.is_equals:
            return '{} = {}'.format(self.index_a, self.format(self.index_b))
        else:
            return '{} ≠ {}'.format(self.index_a, self.format(self.index_b))

class EqualsCompareRange(Predicate):
    def __init__(self, is_equals : bool, index_a : IndexRange, index_b : IndexRange):
        super().__init__()
        self.is_equals : bool = is_equals
        self.index_a : IndexRange = index_a
        self.index_b : IndexRange = index_b

    def transform(self, transformer : AstTransformer) -> EqualsCompareRange:
        return transformer.transform_EqualsCompareRange(self)

    def __str__(self) -> str:
        if self.is_equals:
            return '{} = {}'.format(self.index_a, self.index_b)
        else:
            return '{} ≠ {}'.format(self.index_a, self.index_b)

