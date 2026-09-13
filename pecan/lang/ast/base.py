#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Self
    from pecan.lang.ast_transformer import AstTransformer;
    from pecan.lang.ast.prog import Program, VarRef

class ASTNode:
    def __init__(self):
        self.is_int = False

    def transform(self, transformer : AstTransformer) -> Self:
        raise NotImplementedError('Transform not implemented for {}'.format(self.__class__.__name__))

    def evaluate_node(self, prog : Program):
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

class Expression(ASTNode):
    def __init__(self):
        super().__init__()
        self.is_int : bool = True

    # This should be overriden by all expressions
    def __str__(self) -> str:
        raise NotImplementedError

class UnaryExpression(Expression):
    def __init__(self, a : VarRef):
        super().__init__()
        self.a : VarRef = a

class BinaryExpression(Expression):
    def __init__(self, a : VarRef, b : VarRef):
        super().__init__()
        self.a : VarRef = a
        self.b : VarRef = b
        self.is_int : bool = a.is_int and b.is_int

class Predicate(ASTNode):
    def __init__(self):
        super().__init__()

class TypeHint(ASTNode):
    def __init__(self, type_sink : VarRef, type_source : VarRef, body : Predicate | TypeHint):
        super().__init__()
        self.type_sink : VarRef = type_sink
        self.type_source : VarRef = type_source
        self.body : Predicate | TypeHint = body

    def transform(self, transformer : AstTransformer) -> TypeHint:
        return transformer.transform_TypeHint(self)

    def __str__(self) -> str:
        return '(typ({}) = typ({}) in {})'.format(self.type_sink, self.type_source, self.body)

