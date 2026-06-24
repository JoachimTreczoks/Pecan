#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.automata.automaton import TrueAutomaton, FalseAutomaton
from pecan.lang.ir.base import BinaryIRPredicate, IREvaluation, IRPredicate, UnaryIRPredicate

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.prog import Program

class Conjunction(BinaryIRPredicate):
    def __init__(self, a : IRPredicate, b : IRPredicate):
        super().__init__(a, b)

    def evaluate_node(self, prog : Program) -> IREvaluation:
        a_aut = self.a.evaluate(prog)

        if a_aut.is_empty():
            return a_aut

        b_aut = self.b.evaluate(prog)

        if b_aut.is_empty():
            return b_aut

        return a_aut & b_aut

    def transform(self, transformer : IRTransformer) -> Conjunction:
        return transformer.transform_Conjunction(self)

    def __repr__(self) -> str:
        return '({} ∧ {})'.format(self.a, self.b)

class Disjunction(BinaryIRPredicate):
    def __init__(self, a : IRPredicate, b : IRPredicate):
        super().__init__(a, b)

    def evaluate_node(self, prog : Program) -> IREvaluation:
        a_aut = self.a.evaluate(prog)
        b_aut = self.b.evaluate(prog)

        if a_aut.is_empty():
            return b_aut

        return a_aut | b_aut

    def transform(self, transformer : IRTransformer) -> Disjunction:
        return transformer.transform_Disjunction(self)

    def __repr__(self) -> str:
        return '({} ∨ {})'.format(self.a, self.b)

class Complement(UnaryIRPredicate):
    def __init__(self, a : IRPredicate):
        super().__init__(a)

    def evaluate_node(self, prog : Program) -> IREvaluation:
        return self.a.evaluate(prog).complement()

    def transform(self, transformer : IRTransformer) -> Complement:
        return transformer.transform_Complement(self)

    def __repr__(self) -> str:
        return '(¬{})'.format(self.a)

class BoolConst(IRPredicate):
    def __init__(self, bool_val : bool):
        super().__init__()
        self.bool_val : bool = bool_val

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.bool_val:
            return IREvaluation(TrueAutomaton())
        else:
            return IREvaluation(FalseAutomaton())

    def transform(self, transformer : IRTransformer) -> BoolConst:
        return transformer.transform_BoolConst(self)

    def __repr__(self) -> str:
        if self.bool_val:
            return '⊤'
        else:
            return '⊥'

    def __eq__(self, other : Any) -> bool:
        return other is not None and type(other) is self.__class__ and self.bool_val == other.bool_val

    def __hash__(self) -> int:
        return hash(self.bool_val) # No fields to hash

