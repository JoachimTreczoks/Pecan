#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast.base import BinaryExpression, Expression, Predicate, UnaryExpression

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast.base import TypeHint
    from pecan.lang.ast.prog import Program
    from pecan.lang.ast_transformer import AstTransformer

class Add(BinaryExpression):
    def __init__(self, a : Expression, b : Expression):
        super().__init__(a, b)

    def change_label(self, label : str) -> None: # for changing label to __constant#
        self.label : str = label

    def __str__(self) -> str:
        return '({} + {})'.format(self.a, self.b)

    def transform(self, transformer : AstTransformer) -> Add:
        return transformer.transform_Add(self)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) + self.b.evaluate_int(prog)

class Sub(BinaryExpression):
    def __init__(self, a : Expression, b : Expression):
        super().__init__(a, b)

    def __str__(self) -> str:
        return '({} - {})'.format(self.a, self.b)

    def transform(self, transformer : AstTransformer) -> Sub:
        return transformer.transform_Sub(self)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) - self.b.evaluate_int(prog)

class Mul(BinaryExpression):
    def __init__(self, a : Expression, b : Expression):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> Mul:
        return transformer.transform_Mul(self)

    def __str__(self) -> str:
        return '({} * {})'.format(self.a, self.b)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) * self.b.evaluate_int(prog)

class Div(BinaryExpression):
    def __init__(self, a : Expression, b : Expression):
        super().__init__(a, b)
        if not self.b.is_int:
            raise AutomatonArithmeticError("Second argument of division must be an integer in {}".format(self))

    def __str__(self) -> str:
        return '({} / {})'.format(self.a, self.b)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) // self.b.evaluate_int(prog)

    def transform(self, transformer : AstTransformer) -> Div:
        return transformer.transform_Div(self)

class IntConst(Expression):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val
        self.label : str = "__constant{}".format(self.val)

    def transform(self, transformer : AstTransformer) -> IntConst:
        return transformer.transform_IntConst(self)

    def evaluate_int(self, prog : Program) -> int:
        return self.val

    def __str__(self) -> str:
        return str(self.val)

class Equals(Predicate):
    def __init__(self, a : Expression, b : Expression):
        super().__init__()
        self.a : Expression = a
        self.b : Expression = b

    def transform(self, transformer : AstTransformer) -> Equals:
        return transformer.transform_Equals(self)

    def __str__(self) -> str:
        return '({} = {})'.format(self.a, self.b)

class NotEquals(Predicate):
    def __init__(self, a : Expression, b : Expression):
        super().__init__()
        self.a : Expression = a
        self.b : Expression = b

    def transform(self, transformer : AstTransformer) -> NotEquals:
        return transformer.transform_NotEquals(self)

    def __str__(self) -> str:
        return '({} ≠ {})'.format(self.a, self.b)

class Less(Predicate):
    def __init__(self, a : Expression, b : Expression):
        super().__init__()
        self.a : Expression = a
        self.b : Expression = b

    def transform(self, transformer : AstTransformer) -> Less:
        return transformer.transform_Less(self)

    def __str__(self) -> str:
        return '({} < {})'.format(self.a, self.b)

class Greater(Predicate):
    def __init__(self, a : Expression, b : Expression):
        super().__init__()
        self.a : Expression= a
        self.b : Expression= b

    def transform(self, transformer : AstTransformer) -> Greater:
        return transformer.transform_Greater(self)

    def __str__(self) -> str:
        return '({} > {})'.format(self.a, self.b)

class LessEquals(Predicate):
    def __init__(self, a : Expression, b : Expression):
        super().__init__()
        self.a : Expression = a
        self.b : Expression = b

    def transform(self, transformer : AstTransformer) -> LessEquals:
        return transformer.transform_LessEquals(self)

    def __str__(self) -> str:
        return '({} ≤ {})'.format(self.a, self.b)

class GreaterEquals(Predicate):
    def __init__(self, a : Expression, b : Expression):
        super().__init__()
        self.a : Expression = a
        self.b : Expression = b

    def transform(self, transformer : AstTransformer) -> GreaterEquals:
        return transformer.transform_GreaterEquals(self)

    def __str__(self) -> str:
        return '({} ≥ {})'.format(self.a, self.b)

class Neg(UnaryExpression): # Should this be allowed?
    def __init__(self, a : Expression):
        super().__init__(a)
        self.a : Expression = a

    def transform(self, transformer : AstTransformer) -> Neg:
        return transformer.transform_Neg(self)

    def __str__(self) -> str:
        return '(-{})'.format(self.a)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return -self.a.evaluate_int(prog)

class PredicateExpr(Expression):
    def __init__(self, var_name : str, pred : TypeHint):
        super().__init__()
        self.var_name : str = var_name
        self.pred : TypeHint = pred

    def transform(self, transformer : AstTransformer) -> PredicateExpr:
        return transformer.transform_PredicateExpr(self)

    def __str__(self) -> str:
        return 'Expr({}, {})'.format(self.var_name, self.pred)

class AutomatonArithmeticError(Exception):
    pass

