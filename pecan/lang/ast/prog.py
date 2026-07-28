#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from functools import reduce

from pecan.lang.ast.base import ASTNode, Expression, Predicate

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.automata.automaton import Automaton
    from pecan.lang.ast.bool import Conjunction
    from pecan.lang.ast_transformer import AstTransformer

class VarRef(Expression):
    def __init__(self, var_name : str):
        super().__init__()
        self.var_name : str = var_name
        self.is_int : bool = False

    def transform(self, transformer : AstTransformer) -> VarRef:
        return transformer.transform_VarRef(self)

    def __str__(self) -> str:
        return str(self.var_name)

class AutLiteral(Predicate):
    def __init__(self, aut : Automaton):
        super().__init__()
        self.aut : Automaton = aut
        self.is_int : bool = False

    def transform(self, transformer : AstTransformer) -> AutLiteral:
        return transformer.transform_AutLiteral(self)

    def __str__(self) -> str:
        return 'AUTOMATON LITERAL'

class SpotFormula(Predicate):
    def __init__(self, formula_str : str):
        super().__init__()
        self.formula_str : str = formula_str

    def transform(self, transformer : AstTransformer) -> SpotFormula:
        return transformer.transform_SpotFormula(self)

    def __str__(self) -> str:
        return 'LTL({})'.format(self.formula_str)

class Call(Predicate):
    def __init__(self, name : str, args : list[Expression]):
        super().__init__()
        self.name : str = name
        self.args : list[Expression] = args

    def transform(self, transformer : AstTransformer) -> Call:
        return transformer.transform_Call(self)

    def with_args(self, new_args : list[Expression]) -> Call:
        return Call(self.name, new_args)

    def add_arg(self, new_arg : VarRef) -> Call:
        return Call(self.name, self.args + [new_arg])

    def __str__(self) -> str:
        return '{}({})'.format(self.name, ', '.join(map(str, self.args)))

class NamedPred(ASTNode):
    def __init__(self, name : str, args : list[VarRef | Call], body : Predicate):
        super().__init__()
        self.name : str = name

        self.args : list[VarRef] = []
        self.arg_restrictions : dict[VarRef, Restriction] = {}
        for arg in args:
            if isinstance(arg, VarRef):
                self.args.append(arg)
            elif isinstance(arg, Call):
                var = arg.args[-1]
                self.args.append(var)
                self.arg_restrictions[var] = Restriction([var], arg.with_args(arg.args[:-1]))
            else:
                raise TypeError("Argument '{}' is not: VarRef, or Call!".format(arg))

        self.body : Predicate = body

    def transform(self, transformer : AstTransformer) -> NamedPred:
        return transformer.transform_NamedPred(self)

    def __str__(self) -> str:
        return '{}({}) := {}'.format(self.name, ', '.join(map(str, self.args)), self.body)

class Program(ASTNode):
    def __init__(self, defs, *args, **kwargs : dict[str, Any]): # TODO: Add type hinting for the args and kwargs
        super().__init__()

        self.defs = defs
        self.preds : dict = kwargs.get('preds', {})
        self.context : dict = kwargs.get('context', {})
        self.restrictions : list[dict[VarRef, Restriction]] = kwargs.get('restrictions', [{}])
        self.types : dict = kwargs.get('types', {})
        self.eval_level : int = kwargs.get('eval_level', 0)
        self.result = kwargs.get('result', None)
        self.search_paths : list = kwargs.get('search_paths', [])

    def copy_defaults(self, other_prog : Program) -> Program:
        self.context = other_prog.context
        self.eval_level = other_prog.eval_level
        self.result = other_prog.result
        self.search_paths = other_prog.search_paths
        return self

    def extract_implications(self) -> None:
        from pecan.lang.ast.praline import PralineDirective
        from pecan.lang.ast.directives import DirectiveLoadAut

        restrict : dict[str, Call] = {}
        for d in self.defs:
            if isinstance(d, PralineDirective):
                if d.name == 'Theorem':
                    a, b = self.extract_implication(restrict, d.term.vals[1].pecan_term)
                    safe_name = d.term.vals[0].val.replace(' ', '_').replace('.', '')

                    if a is not None and b is not None:
                        print('Implication ("{}", {{{}}}, {{{}}}).'.format(safe_name, a, b))
            elif isinstance(d, DirectiveLoadAut):
                print(d)
            elif isinstance(d, Restriction):
                for v in d.restrict_vars:
                    if v.var_name in restrict:
                        restrict[v.var_name].append(d.pred.add_arg(v))
                    else:
                        restrict[v.var_name] = [d.pred.add_arg(v)]

    def extract_implication(self, restrict : dict[str, Call], term : Predicate) -> tuple[Conjunction | None, Predicate]:
        from pecan.lang.ast.quant import Forall
        from pecan.lang.ast.bool import Implies, Conjunction, BoolConst
        from pecan.lang.ast.annotation import Annotation
        if isinstance(term, Forall):
            cs = [ cond for cond in term.conds if cond is not None ]
            for v in term.vars:
                cs.extend(restrict.get(v.var_name, []))
            if len(cs) == 0:
                lhs = BoolConst(True)
            else:
                lhs = reduce(Conjunction, cs)
            l1, r1 = self.extract_implication(restrict, term.pred)
            if l1 is None:
                return lhs, r1
            else:
                return Conjunction(lhs, l1), r1
        elif isinstance(term, Implies):
            l1, r1 = self.extract_implication(restrict, term.b)
            if l1 is None:
                return term.a, r1
            else:
                return Conjunction(term.a, l1), r1
        elif isinstance(term, Annotation):
            return self.extract_implication(restrict, term.body)
        else:
            return None, term

    def transform(self, transformer : AstTransformer) -> Program:
        return transformer.transform_Program(self)

    def __str__(self) -> str:
        return str(self.defs)

class Restriction(ASTNode):
    def __init__(self, restrict_vars : list[VarRef | str], pred : Call):
        super().__init__()
        self.restrict_vars : list[VarRef] = []
        for var in restrict_vars:
            if isinstance(var, VarRef):
                self.restrict_vars.append(var)
            else:
                raise TypeError("Argument '{}' is not a valid VarRef".format(var))
        self.pred : Call = pred

    def transform(self, transformer : AstTransformer) -> Restriction:
        return transformer.transform_Restriction(self)

    def __str__(self) -> str:
        return '{} are {}'.format(', '.join(map(str, self.restrict_vars)), self.pred)

