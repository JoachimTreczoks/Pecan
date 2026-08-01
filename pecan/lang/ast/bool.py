#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast.base import Predicate

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast.base import ASTNode
    from pecan.lang.ast_transformer import AstTransformer

class Conjunction(Predicate):
    def __init__(self, a : ASTNode, b : ASTNode):
        super().__init__()
        self.a : ASTNode = a
        self.b : ASTNode = b

    def transform(self, transformer : AstTransformer) -> Conjunction:
        return transformer.transform_Conjunction(self)

    def __str__(self) -> str:
        return '({} ∧ {})'.format(self.a, self.b)

class Disjunction(Predicate):
    def __init__(self, a : ASTNode, b : ASTNode):
        super().__init__()
        self.a : ASTNode = a
        self.b : ASTNode = b

    def transform(self, transformer : AstTransformer) -> Disjunction:
        return transformer.transform_Disjunction(self)

    def __str__(self) -> str:
        return '({} ∨ {})'.format(self.a, self.b)

class Complement(Predicate):
    def __init__(self, a : ASTNode):
        super().__init__()
        self.a : ASTNode = a

    def transform(self, transformer : AstTransformer) -> Complement:
        return transformer.transform_Complement(self)

    def __str__(self) -> str:
        return '(¬{})'.format(self.a)

class Iff(Predicate):
    def __init__(self, a : ASTNode, b : ASTNode):
        super().__init__()
        self.a : ASTNode = a
        self.b : ASTNode = b

    def transform(self, transformer : AstTransformer) -> Iff:
        return transformer.transform_Iff(self)

    def __str__(self) -> str:
        return '({} ⟺  {})'.format(self.a, self.b)

class Implies(Predicate):
    def __init__(self, a : ASTNode, b : ASTNode):
        super().__init__()
        self.a : ASTNode = a
        self.b : ASTNode = b

    def transform(self, transformer : AstTransformer) -> Implies:
        return transformer.transform_Implies(self)

    def __str__(self) -> str:
        return '({} ⟹  {})'.format(self.a, self.b)

class BoolConst(Predicate):
    def __init__(self, bool_val : bool):
        super().__init__()
        self.bool_val : bool = bool_val

    def transform(self, transformer : AstTransformer) -> BoolConst:
        return transformer.transform_BoolConst(self)

    def __str__(self) -> str:
        if self.bool_val:
            return '⊤'
        else:
            return '⊥'

