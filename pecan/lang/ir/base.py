#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import time

from pecan.settings import settings
from pecan.automata.automaton import Automaton

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any, Literal, Self, Iterable
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.type_inference import Type
    from pecan.lang.ir.prog import Program, VarRef
    from pecan.utility import VarMap

class IRNode:
    id = 0
    @staticmethod
    def fresh_name() -> str:
        label = f"__pecan_var{IRNode.id}"
        IRNode.id += 1
        return label

    def __init__(self):
        from pecan.lang.type_inference import UndefinedType
        # TODO: detect used labels and avoid those
        self.label : None | str = None
        self.type : Type = UndefinedType()
        assert self.type == UndefinedType()

    def label_var(self) -> VarRef:
        from pecan.lang.ir.prog import VarRef
        if self.label is None:
            self.label = IRNode.fresh_name()
        return VarRef(self.label).with_type(self.get_type())

    def with_type(self, new_type : None | Type) -> Self:
        from pecan.lang.type_inference import UndefinedType
        self.type : Type = new_type or UndefinedType()
        return self

    def get_type(self) -> Type:
        return self.type

    def show_aut_stats(self, prog : Program, aut : Automaton, desc : None | str = None) -> None:
        sn, en = aut.num_states(), aut.num_edges()

        if desc is None:
            settings.log(1, lambda: self.indented(prog, 'Automaton has {} states and {} edges'.format(sn, en)))
        else:
            settings.log(1, lambda: self.indented(prog, 'Automaton has {} states and {} edges {}'.format(sn, en, desc)))

    def indented(self, prog : Program, s : str) -> str:
        return '{}{}'.format(' ' * prog.eval_level, s)

    def simplify(self, prog : Program, evaluation : IREvaluation) -> IREvaluation:
        self.show_aut_stats(prog, evaluation.aut, desc='before simplify')

        evaluation.simplify_edges()
        self.show_aut_stats(prog, evaluation.aut, desc='after simplify_edges')

        evaluation.simplify_states()
        self.show_aut_stats(prog, evaluation.aut, desc='after simplify_states')

        return evaluation

    def get_display_node(self, prog : Program) -> Self:
        return self

    def evaluate(self, prog : Program) -> IREvaluation:
        prog.eval_level += 1

        start_time = time.time()

        result = self.evaluate_node(prog)
        if not isinstance(result, IREvaluation):
            raise Exception('Not an evaluation, error from{}'.format(type(self)))
        sn = result.num_states()
        en = result.num_states()

        if sn >= 0 and en >= 0:
            result = self.simplify(prog, result)

        prog.eval_level -= 1

        sn = result.num_states()
        en = result.num_states()

        end_time = time.time()

        if settings.should_write_statistics():
            prog.update_max_aut(sn, en, end_time - start_time)

        if settings.get_debug_level() > 0 and sn >= 0 and en >= 0:
            settings.log(0, lambda: self.indented(prog, '{} has {} states and {} edges ({:.2f} seconds)'.format(self.get_display_node(prog), sn, en, end_time - start_time)))

        return result

    def transform(self, transformer : IRTransformer) -> Self:
        raise NotImplementedError('Transform not implemented for {}'.format(self.__class__.__name__))

    def evaluate_node(self, prog : Program) -> IREvaluation:
        raise NotImplementedError

class IRExpression(IRNode):
    def __init__(self):
        super().__init__()
        self.is_int : bool = True

    def evaluate_node(self, prog : Program) -> Automaton | tuple[Automaton, VarRef]:
        raise NotImplementedError
    
    def evaluate_int(self, prog : Program) -> int:
        raise NotImplementedError

    # This should be overriden by all expressions
    def __str__(self) -> str:
        raise NotImplementedError

    def format_type(self, string : str) -> str:
        from pecan.lang.type_inference import UndefinedType
        if self.type == UndefinedType():
            return string
        else:
            return f'{string} : {self.get_type()}'

class UnaryIRExpression(IRExpression):
    def __init__(self, a):
        super().__init__()
        self.a = a

    def with_type(self, new_type : Type) -> UnaryIRExpression:
        self.a = self.a.with_type(new_type)
        return super().with_type(new_type)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a and self.get_type() == other.get_type()

    def __hash__(self) -> int:
        return hash((self.a, self.get_type()))

class BinaryIRExpression(IRExpression):
    def __init__(self, a, b):
        super().__init__()
        self.is_int = a.is_int and b.is_int
        self.a = a
        self.b = b

    def with_type(self, new_type : None | Type) -> Self:
        self.a = self.a.with_type(new_type)
        self.b = self.b.with_type(new_type)
        return super().with_type(new_type)

    def project_intermediates(self, prog : Program, val_a : VarRef, val_b : VarRef, aut : Automaton) -> Automaton:
        from pecan.lang.ir.prog import VarRef

        proj_vars = set()

        if not isinstance(self.a, VarRef):
            proj_vars.add(val_a)

        if not isinstance(self.b, VarRef):
            proj_vars.add(val_b)

        return aut.project(proj_vars, prog.get_var_map())

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a and self.b == other.b and self.get_type() == other.get_type()

    def __hash__(self) -> int:
        return hash((self.a, self.b, self.get_type()))

class IRPredicate(IRNode):
    def __init__(self):
        super().__init__()

    def evaluate_node(self, prog : Program) -> Automaton:
        raise NotImplementedError
    
class IRComparison(IRPredicate):
    def __init__(self, a : IRExpression, b : IRExpression):
        super().__init__()
        self.a : IRExpression = a
        self.b : IRExpression = b

    def project_intermediates(self, prog : Program, val_a : VarRef, val_b : VarRef, aut : Automaton) -> Automaton:
        from pecan.lang.ir.prog import VarRef

        proj_vars : set[VarRef] = set()

        if not isinstance(self.a, VarRef):
            proj_vars.add(val_a)

        if not isinstance(self.b, VarRef):
            proj_vars.add(val_b)

        return aut.project(proj_vars, prog.get_var_map())

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a and self.b == other.b

    def __hash__(self) -> int:
        return hash((self.a, self.b))

class BinaryIRPredicate(IRPredicate):
    def __init__(self, a : IRPredicate, b : IRPredicate):
        super().__init__()
        self.a : IRPredicate = a
        self.b : IRPredicate = b

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a and self.b == other.b

    def __hash__(self) -> int:
        return hash((self.a, self.b))

class UnaryIRPredicate(IRPredicate):
    def __init__(self, a : IRPredicate):
        super().__init__()
        self.a : IRPredicate = a

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a

    def __hash__(self) -> int:
        return hash(self.a)

class TypeHint(IRNode):
    def __init__(self, expr_a, expr_b, body):
        super().__init__()
        self.expr_a = expr_a
        self.expr_b = expr_b
        self.body = body

    def transform(self, transformer : IRTransformer) -> TypeHint:
        return transformer.transform_TypeHint(self)

    def __str__(self) -> str:
        return '(typ({}) = typ({}) in {})'.format(self.expr_a, self.expr_b, self.body)

class IREvaluation:
    def __init__(self, aut : Automaton, ref : None | VarRef = None):
        if not isinstance(aut, Automaton):
            raise Exception('Not an aut, instead got {}'.format(type(aut)))
        self.aut : Automaton = aut
        self.ref : None | VarRef = ref

    def with_ref(self, ref : VarRef) -> IREvaluation:
        self.ref = ref
        return self
    
    def get_aut_type(self) -> str:
        return self.aut.get_aut_type()
    
    def get_var_map(self) -> VarMap:
        return self.aut.get_var_map()
    
    def conjunction(self, other : IREvaluation) -> IREvaluation:
        self.aut = self.aut.conjunction(other.aut)
        return self

    def disjunction(self, other : IREvaluation) -> IREvaluation:
        self.aut = self.aut.disjunction(other.aut)
        return self

    def complement(self) -> IREvaluation:
        self.aut = self.aut.complement()
        return self

    def substitute(self, arg_map : dict[str, str], env_var_map : VarMap) -> IREvaluation:
        return IREvaluation(self.aut.substitute(arg_map, env_var_map), self.ref) # This can not mutate `self`, otherwise Pecan breaks down *bad*

    def project(self, var_refs : Iterable[VarRef], env_var_map : VarMap) -> IREvaluation:
        self.aut = self.aut.project(var_refs, env_var_map)
        return self

    def is_empty(self) -> bool:
        return self.aut.is_empty()

    def truth_value(self) -> Literal['false', 'true', 'sometimes']:
        return self.aut.truth_value()

    def num_states(self) -> int:
        return self.aut.num_states()
    
    def num_edges(self) -> int:
        return self.aut.num_edges()
    
    def accepting_word(self) -> dict | None:
        return self.aut.accepting_word()
    
    def postprocess(self, level : str | None = None) -> IREvaluation:
        self.aut = self.aut.postprocess(level)
        return self
    
    def simplify_states(self) -> IREvaluation:
        self.aut = self.aut.simplify_states()
        return self
    
    def simplify_edges(self) -> IREvaluation:
        self.aut = self.aut.simplify_edges()
        return self
    
    def merge_states(self) -> IREvaluation:
        self.aut = self.aut.merge_states()
        return self
    
    def merge_edges(self) -> IREvaluation:
        self.aut = self.aut.merge_edges()
        return self
    
    def relabel(self) -> IREvaluation:
        self.aut = self.aut.relabel()
        return self
    
    def __and__(self, other : IREvaluation) -> IREvaluation:
        self.aut = self.aut & other.aut
        return self

    def __or__(self, other : IREvaluation) -> IREvaluation:
        self.aut = self.aut | other.aut
        return self


