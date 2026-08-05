#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from colorama import Fore, Style

import os
from functools import reduce

import spot

from typing import TypedDict

from pecan.tools.hoa_loader import from_spot_aut
from pecan.lang.ir.base import *
from pecan.settings import settings
from pecan.logger import Logger
from pecan.utility import VarMap
from pecan.exceptions import CallResolvingError, MatchingError, UnificationError

from pecan.lang.ir.bool import BoolConst

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.type_inference import RestrictionType
    from pecan.lang.ir.base import IREvaluation
    from pecan.lang.ir.praline.base import PralineTerm
    from pecan.lang.ir.praline.functional import Closure, PralineAlias

class VarRef(IRExpression):
    def __init__(self, var_name : str):
        super().__init__()
        self.var_name : str = var_name
        self.is_int : bool = False

    def evaluate(self, prog) -> IREvaluation:
        # The automata accepts everything (because this isn't a predicate)
        from pecan.lang.ir.bool import BoolConst
        return BoolConst(True).evaluate(prog).with_ref(self)

    def transform(self, transformer : IRTransformer) -> VarRef:
        return transformer.transform_VarRef(self)

    def __str__(self) -> str:
        return self.var_name
    
    def __repr__(self) -> str: # Needed because Guido van Rossum decided to reject https://peps.python.org/pep-3140/ 18 years ago and never reconsidered...
        return self.__str__()

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var_name == other.var_name

    def __hash__(self) -> int:
        return hash(self.var_name)

class AutLiteral(IRPredicate):
    def __init__(self, aut : Automaton | IREvaluation, display_node : IRNode | None = None):
        super().__init__()
        if isinstance(aut, Automaton):
            self.aut : Automaton = aut
        elif isinstance(aut, IREvaluation):
            self.aut : Automaton = aut.aut
        self.is_int : bool = False
        self.display_node : IRNode | None = display_node # Currently completely unused, as nothing ever instantiates AutLiterals with one

    def evaluate(self, prog : Program) -> IREvaluation:
        return IREvaluation(self.aut)

    def transform(self, transformer : IRTransformer) -> AutLiteral:
        return transformer.transform_AutLiteral(self)

    def __str__(self) -> str:
        if self.display_node is not None:
            return 'AutLiteral({})'.format(str(self.display_node))
        else:
            return 'AUTOMATON LITERAL'

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.aut == other.aut

    def __hash__(self) -> int:
        return hash((self.aut))

class SpotFormula(IRPredicate):
    def __init__(self, formula_str : str):
        super().__init__()
        self.formula_str : str = formula_str

    def evaluate(self, prog : Program) -> IREvaluation:
        try:
            return IREvaluation(from_spot_aut(spot.translate(self.formula_str)))
        except:
            return IREvaluation(from_spot_aut(spot.parse_word(self.formula_str).as_automaton()))

    def transform(self, transformer : IRTransformer) -> SpotFormula:
        return transformer.transform_SpotFormula(self)

    def __str__(self) -> str:
        return 'LTL({})'.format(self.formula_str)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.formula_str == other.formula_str

    def __hash__(self) -> int:
        return hash((self.formula_str))

class Match:
    def __init__(self, pred_name : None | str = None, pred_args : list[VarRef] | None = None, match_any : bool = False):
        self.pred_name : None | str = pred_name
        self.pred_args : list[VarRef] = pred_args or []
        self.match_any : bool = match_any

    def arity(self) -> int:
        return len(self.pred_args)

    def unify(self, other : Match) -> Match:
        if other.match_any:
            return self
        if self.match_any:
            return other

        new_args = []
        if self.pred_name != other.pred_name or self.arity() != other.arity():
            raise UnificationError('Could not unify {} and {}'.format(self, other))

        for arg1, arg2 in zip(self.pred_args, other.pred_args):
            if arg1 == 'any' and arg2 == 'any':
                new_args.append('any')
            elif arg1 == 'any' and arg2 != 'any':
                new_args.append(arg2)
            elif arg1 != 'any' and arg2 == 'any':
                new_args.append(arg1)
            else:
                if arg1 == arg2:
                    new_args.append(arg1)
                else:
                    raise UnificationError('Could not unify {} and {}: cannot unify {} and {}'.format(self, other, arg1, arg2))

        return Match(self.pred_name, new_args)

    def call_with(self, pred_name : str, unification : dict[str, str], rest_args : list[VarRef]) -> Call:
        if self.match_any:
            raise CallResolvingError('Predicate not found: {}'.format(pred_name))
        i = 0
        final_args : list[VarRef] = []
        for arg in self.pred_args:
            if arg.var_name == 'any':
                if i >= len(rest_args):
                    # TODO: We should check this in the linter probably
                    raise CallResolvingError('Not enough arguments to call {}: {}'.format(self, rest_args))

                final_args.append(rest_args[i])
                i += 1
            else:
                final_args.append(VarRef(unification.get(arg.var_name, arg.var_name)))

        if not self.pred_name:
            raise CallResolvingError('Missing predicate name')
        return Call(self.pred_name, final_args)

    def __str__(self) -> str:
        return '{}({})'.format(self.pred_name, ', '.join(map(str, self.pred_args)))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.pred_name == other.pred_name and self.pred_args == other.pred_args and self.match_any == other.match_any

    def __hash__(self) -> int:
        return hash((self.pred_name, self.pred_args, self.match_any))

class Call(IRPredicate):
    def __init__(self, name : str, args : list[VarRef]):
        super().__init__()
        self.name : str = name
        self.args : list[VarRef] = args

    def arity(self) -> int:
        return len(self.args)

    def match(self) -> Match:
        return Match(self.name, self.args)

    def with_args(self, new_args : list[VarRef]) -> Call:
        return Call(self.name, new_args)

    def add_arg(self, new_arg : VarRef) -> Call:
        return Call(self.name, self.args + [new_arg]).with_type(self.get_type())

    def subs_last(self, new_arg : VarRef) -> Call:
        return self.with_args(self.args[:-1] + [new_arg]).with_type(self.get_type())

    def evaluate_node(self, prog : Program) -> IREvaluation:
        return prog.call(self.name, self.args)

    def transform(self, transformer : IRTransformer) -> Call:
        return transformer.transform_Call(self)

    def __str__(self) -> str:
        return '{}({})'.format(self.name, ', '.join(map(str, self.args)))
    
    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.name == other.name and self.args == other.args

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.args)))

class NamedPred(Call):
    def __init__(self, name : str,
                 args : list[VarRef],
                 arg_restrictions : dict,
                 body : IRPredicate,
                 restriction_env : dict | None = None,
                 body_evaluated : IREvaluation | None = None,
                 arg_name_map : dict | None = None):
        super().__init__(name, args)

        self.arg_restrictions : dict = arg_restrictions
        self.body : IRPredicate = body

        self.restriction_env : dict = restriction_env or {}
        self.body_evaluated : IREvaluation | None = body_evaluated
        self.arg_name_map : dict = arg_name_map or {}

    def evaluate(self, prog : Program) -> IREvaluation:
        # Here we keep track of all restrictions that were in scope when we are evaluated;
        # this essentially builds a closure. Otherwise, if we forget a variable after the declaration of this predicate,
        # then we will lose the restriction when we are called. This would cause our behavior to depend on lexically
        # where this predicate is used in the program, which would be confusing.
        prog.enter_scope()

        try:
            for _, arg_restriction in self.arg_restrictions.items():
                arg_restriction.evaluate(prog)

            self.restriction_env = prog.get_restriction_env()

            from pecan.lang.optimizer.tools import FreeVars
            free_vars = FreeVars().analyze(self.body)
            diff = free_vars - set(arg.var_name for arg in self.args)
            if len(diff) > 0:
                Logger.warn("Free variables found in {}: {}".format(self.name, diff))
        finally:
            prog.exit_scope()

        return BoolConst(True).evaluate(prog) # Dummy return value, to allow keeping notation simple throughout the rest of the IR codebase

    def transform(self, transformer : IRTransformer) -> NamedPred:
        return transformer.transform_NamedPred(self)

    def arity(self) -> int:
        return len(self.args)

    def match(self) -> Match:
        return Match(self.name, [VarRef('any')] * self.arity())

    def call(self, prog : Program, arg_names : list[VarRef] | None = None) -> IREvaluation:
        prog.enter_scope(dict(self.restriction_env))

        try:
            if self.body_evaluated is None:
                # TODO: START AND FINISH HERE!!!!
                if settings.should_write_statistics():
                    prog.start_max_aut(self.name)

                self.body_evaluated = self.body.evaluate(prog).relabel()

                if settings.should_write_statistics():
                    sn, en, runtime = prog.finish_max_aut(self.name)
                    sn = max(self.body_evaluated.num_states(), sn)
                    en = max(self.body_evaluated.num_edges(), en)
                    Logger.info('Max states for {} is {}'.format(self.name, sn))
                    Logger.info('Max edges for {} is {}'.format(self.name, en))
                    Logger.info('Runtime for {} is {}'.format(self.name, runtime))

            if not arg_names:
                return self.body_evaluated
            else:
                if len(arg_names) < len(self.args):
                    raise CallResolvingError('Not enough arguments for {}. Expected {}, got {}'.format(self.name, len(self.args), len(arg_names)))
                subs_dict = {arg.var_name: name.var_name for arg, name in zip(self.args, arg_names)}
                return self.body_evaluated.substitute(subs_dict, prog.get_var_map())
        finally:
            prog.exit_scope()

    def __str__(self) -> str:
        if self.body_evaluated is None:
            return '{}({}) := {}'.format(self.name, ', '.join(map(str, self.args)), self.body)
        else:
            return '{}({}) := {} (evaluated)'.format(self.name, ', '.join(map(str, self.args)), self.body)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.name == other.name and self.args == other.args and self.arg_restrictions == other.arg_restrictions and self.body == other.body and self.restriction_env == other.restriction_env

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.args)))

class Program(IRNode):
    def __init__(self, defs, *args, **kwargs):
        super().__init__()

        self.defs : list[IRNode] = defs
        self.preds : dict[str, NamedPred] = kwargs.get('preds', {})
        self.context : dict[str, str] = kwargs.get('context', {})
        self.restrictions : list[dict[str, list[Call]]] = kwargs.get('restrictions', [{}])
        self.global_restrictions : dict[str, list[Call]] = kwargs.get('global_restrictions', {})
        self.types : dict[RestrictionType, dict[str, Call]] = kwargs.get('types', {})
        self.eval_level : int = kwargs.get('eval_level', 0)
        self.result : None | Result = kwargs.get('result', None)
        self.search_paths : list[str] = kwargs.get('search_paths', [])

        self.praline_envs : list[dict[str, PralineTerm]] = kwargs.get('praline_envs', [])
        self.praline_defs : dict[str, Closure] = kwargs.get('praline_defs', {})
        self.praline_aliases : dict[str, PralineAlias] = kwargs.get('praline_aliases', {})

        # The current to-process index in self.defs
        # This is used for emitting new definitions via Praline (see Program.emit_definition and pecan.lib.praline.builtins.Emit)
        self.idx : int = 0
        self.emit_offset : int = 0

        self.aut_stats : dict[str, AutomatonStats] = {}

        self.var_map : list[VarMap] = []

        self.generated_files : list[str] = kwargs.get('generated_files', [])

        from pecan.lang.type_inference import TypeInferer
        self.type_inferer : TypeInferer = TypeInferer(self)

    def start_max_aut(self, name : str) -> Program:
        self.aut_stats[name] = { 'states': 0, 'edges': 0, 'runtime': 0 }
        return self

    def finish_max_aut(self, name : str) -> tuple[int, int, float]:
        stats = self.aut_stats.pop(name)
        return stats['states'], stats['edges'], stats['runtime']

    def update_max_aut(self, sn : int, en : int, runtime : float) -> None:
        for name in self.aut_stats:
            if sn > self.aut_stats[name]['states']:
                self.aut_stats[name]['states'] = sn
                self.aut_stats[name]['edges'] = en

            self.aut_stats[name]['runtime'] = max(self.aut_stats[name]['runtime'], runtime)

    def get_var_map(self) -> VarMap:
        return self.var_map[-1]

    def enter_praline_env(self, new_env = None) -> None:
        self.praline_envs.append(new_env or {})

    def exit_praline_env(self) -> dict[str, PralineTerm]:
        return self.praline_envs.pop()

    def praline_lookup(self, name : str) -> PralineTerm:
        if name in self.praline_envs[-1]:
            return self.praline_envs[-1][name]

        if name in self.praline_defs:
            return self.praline_defs[name]

        if name in self.preds:
            from pecan.lang.ir.praline import PralineString
            return PralineString(name)

        raise ValueError('Unknown symbol: "{}"'.format(name))

    def praline_env_clone(self) -> dict:
        return dict(self.praline_envs[-1])

    def define_alias(self, name : str, alias : PralineAlias) -> None:
        self.praline_aliases[name] = alias

    def lookup_alias(self, name : str) -> PralineAlias:
        if name in self.praline_aliases:
            return self.praline_aliases[name]
        else:
            raise ValueError('Unknown alias name: {}'.format(name))

    def praline_define(self, name : str, val : Closure) -> None:
        self.praline_defs[name] = val

    def praline_local_define(self, name : str, val : PralineTerm) -> None:
        self.praline_envs[-1][name] = val

    def praline_local_define_all(self, env : dict[str, PralineTerm]) -> None:
        self.praline_envs[-1].update(env)

    def praline_local_cleanup(self, names : Iterable[str]) -> None:
        for name in names:
            self.praline_envs[-1].pop(name)

    def copy_defaults(self, other_prog : Program) -> Program:
        self.context = other_prog.context
        self.eval_level = other_prog.eval_level
        self.result = other_prog.result
        self.search_paths.extend(other_prog.search_paths)
        return self

    def include(self, other_prog : Program) -> None:
        # Note: Intentionally do NOT merge restrictions, because it would be super confusing if variable restrictions "leaked" from imports
        self.preds.update(other_prog.preds)
        self.context.update(other_prog.context)
        self.types.update(other_prog.types)

        self.praline_defs.update(other_prog.praline_defs)
        self.praline_aliases.update(other_prog.praline_aliases)

        self.generated_files.extend(other_prog.generated_files)

    def add_generated_file(self, path : str) -> None:
        self.generated_files.append(path)

    def get_generated_files(self) -> list[str]:
        return self.generated_files

    def include_with_restrictions(self, other_prog : Program) -> None:
        self.include(other_prog)

        self.global_restrictions.update(other_prog.global_restrictions)

    def declare_type(self, pred_ref : RestrictionType, val_dict : dict[str, Call]) -> None:
        self.types[pred_ref] = val_dict

    def type_infer[T : IRNode](self, node : T) -> T:
        return self.type_inferer.reset().transform(node)

    def emit_definition(self, d : IRNode) -> None:
        self.emit_offset += 1
        self.defs.insert(self.idx + self.emit_offset, d)
        self.run_definition(self.idx + self.emit_offset, d)

    def run_definition(self, i : int, d : IRNode) -> IREvaluation | None:
        from pecan.lang.typed_ir_lowering import TypedIRLowering
        from pecan.lang.optimizer.optimizer import Optimizer

        if isinstance(d, NamedPred):
            Logger.debug('Type inference and IR lowering for: {}'.format(d.name), 1)
            transformed_def = TypedIRLowering(self).transform(self.type_infer(d))

            if settings.opt_enabled():
                Logger.debug('Performing typed optimization on: {}'.format(d.name), 1)
                transformed_def = Optimizer(self).optimize(transformed_def)

            transformed_def = TypedIRLowering(self).transform(transformed_def)

            Logger.log('Lowered IR:', 1)
            Logger.log(str(transformed_def), 1)

            self.defs[i] = transformed_def
            self.preds[d.name] = transformed_def
            self.preds[d.name].evaluate(self)
            Logger.log(str(self.preds[d.name]), 0)
        else:
            return d.evaluate(self)
        
    def evaluate_prog(self, old_env : Program | None = None) -> Program:
        from pecan.lib.praline.builtins import builtins

        for builtin in builtins:
            builtin.evaluate(self)

        if old_env is not None:
            self.include(old_env)

        succeeded = True
        msgs = []
        self.idx = 0

        # Don't use a for, because Praline code can insert new definitions dynamically
        while self.idx < len(self.defs):
            self.enter_var_map_scope()

            self.emit_offset = 0
            d = self.defs[self.idx]

            Logger.debug('Processing: {}'.format(d))
            result = self.run_definition(self.idx, d)
            if result is not None and isinstance(result, Result):
                if result.failed():
                    succeeded = False
                    msgs.append(result.message())

            self.idx += 1 + self.emit_offset

            self.exit_var_map_scope()

        # Clear all restrictions. All relevant restrictions will be held inside the restriction_env of the relevant predicates.
        # Having them also in our restrictions list just leads to double restricting, which is a waste of computation time
        self.restrictions.clear()
        self.idx = 0

        self.result = Result('\n'.join(msgs), succeeded)

        return self

    def transform(self, transformer : IRTransformer) -> Program:
        return transformer.transform_Program(self)

    def forget(self, var_name : str) -> None:
        self.restrictions[-1].pop(var_name)

    def forget_global(self, var_name : str) -> None:
        self.global_restrictions.pop(var_name)

    def global_restrict(self, var_name : str, pred : Call) -> None:
        if pred is not None and pred not in self.get_restrictions(var_name):
            if not isinstance(pred, Call) or not pred.args:
                raise CallResolvingError('Unexpected predicate used as restriction (must be Call with the first argument as the variable to restrict): {}'.format(pred))

            if var_name in self.global_restrictions:
                self.global_restrictions[var_name].append(pred)
            else:
                self.global_restrictions[var_name] = [pred]

    def restrict(self, var_name : str, pred : Call) -> None:
        if pred is not None and pred not in self.get_restrictions(var_name, local_only=True):
            if not isinstance(pred, Call) or not pred.args:
                raise CallResolvingError('Unexpected predicate used as restriction (must be Call with the first argument as the variable to restrict): {}'.format(pred))

            if var_name in self.restrictions[-1]:
                self.restrictions[-1][var_name].append(pred)
            else:
                self.restrictions[-1][var_name] = [pred]

    def get_restriction_env(self, local_only : bool = False) -> dict[str, list[Call]]:
        result = {}
        if not local_only:
            result.update(self.global_restrictions)
        result.update(self.restrictions[-1])

        return result

    def enter_scope(self, new_restrictions : dict | None = None) -> None:
        self.restrictions.append(dict(new_restrictions or {}))

    def exit_scope(self) -> None:
        if self.restrictions:
            self.restrictions.pop(-1)
        else:
            raise RuntimeError('Cannot exit the last scope!')

    def enter_var_map_scope(self, var_map : VarMap | None = None) -> None:
        self.var_map.append(var_map or VarMap())

    def exit_var_map_scope(self) -> VarMap:
        return self.var_map.pop()

    def get_restrictions(self, var_name: str, local_only : bool = False) -> list[IRPredicate]:
        result = []
        # for scope in self.restrictions:
        for r in self.get_restriction_env(local_only).get(var_name, []):
            if not r in result:
                result.append(r)
        return result

    def call(self, pred_name : str, args : list[VarRef] | None = None) -> IREvaluation:
        """Returns the evaluation of a saved predicate, using type-specific predicates if typed arguments are given"""
        try:
            if not args:
                if pred_name in self.preds:
                    return self.preds[pred_name].call(self, args)
                else:
                    raise CallResolvingError('Predicate {}({}) not found (known predicates: {}!'.format(pred_name, args, self.preds.keys()))
            else:
                return self.dynamic_call(pred_name, args)
        except CallResolvingError as e:
            if pred_name in self.context:
                return self.call(self.context[pred_name], args)
            else:
                raise e

    def unify_with(self, a : str, b : str, unification : dict[str, str]) -> bool:
        if b in unification:
            return unification[b] == a
        else:
            unification[b] = a
            return True

    def unify_type(self, t1 : Call | VarRef | None, t2 : Call | VarRef | None, unification : dict[str, str]) -> bool:
        """Returns true if the unification of the types of the two given parameters was successful"""
        if isinstance(t1, VarRef) and isinstance(t2, VarRef):
            return self.unify_with(t1.var_name, t2.var_name, unification)
        elif isinstance(t1, Call) and isinstance(t2, Call):
            if t1.name != t2.name or len(t1.args) != len(t2.args):
                return False

            for arg1, arg2 in zip(t1.args, t2.args):
                if not self.unify_type(arg1, arg2, unification):
                    return False

            return True
        else:
            return False

    def try_unify_type(self, t1 : Call | VarRef | None, t2 : Call | VarRef | None, unification : dict[str, str]) -> bool:
        """Returns true if the unification of the types of the two given parameters was successful, wrapping `self.unify_type()` to undo unwanted changes"""
        old_unification = dict(unification)
        result = self.unify_type(t1, t2, unification)
        if result:
            return result
        else:
            # Do it this way so we mutate `unification` itself, and we don't want to change it unless we successfully unify
            unification.clear()
            unification.update(old_unification)
            return False

    def lookup_pred_by_name(self, pred_name : str) -> NamedPred:
        """Returns a predicate of the given name if it exists"""
        if pred_name in self.preds:
            return self.preds[pred_name]
        else:
            raise CallResolvingError('Predicate {} not found (known predicates: {}!'.format(pred_name, self.preds.keys()))

    def lookup_call(self, pred_name : str, arg : VarRef, unification : dict[str, str]) -> Match:
        """Returns the closest fitting match for a given predicate"""
        from pecan.lang.type_inference import UndefinedType
        if arg.get_type() == UndefinedType():
            return Match(match_any=True)

        for t in self.types:
            restriction = arg.get_type().restrict(arg)
            if self.try_unify_type(restriction, t.restrict(arg), unification):

                if pred_name in self.types[t]:
                    return self.types[t][pred_name].match()
                else:
                    return Match(match_any=True)

        return Match(match_any=True)

    def lookup_dynamic_call(self, pred_name : str, args : list[VarRef]) -> Call:
        """Returns the closest fitting Call for a predicate of given name and parameters"""
        matches : list[Match] = []
        unification : dict[str, str] = {}
        for arg in args:
            match = self.lookup_call(pred_name, arg, unification)
            if match is None:
                raise MatchingError('No matching predicate found for {} called {}'.format(arg, pred_name))
            matches.append(match)

        # There will always be at least one match because there should always be
        # at least one argument, so no need for an initial value
        final_match = reduce(lambda a, b: a.unify(b), matches, Match(match_any=True))

        # Match any means that we didn't find any type-specific matches
        if final_match.match_any:
            return Call(pred_name, args)
        else:
            return final_match.call_with(pred_name, unification, args)

    def dynamic_call(self, pred_name : str, args : list[VarRef]) -> IREvaluation:
        """Returns the evaluation of a predicate, using type-specific predicates if possible"""
        final_call = self.lookup_dynamic_call(pred_name, args)
        return self.lookup_pred_by_name(final_call.name).call(self, final_call.args)

    def locate_file(self, filename : str) -> str:
        for path in self.search_paths:
            try_path = os.path.join(path, filename)
            if os.path.exists(try_path):
                return try_path

        raise FileNotFoundError(filename)

    def __str__(self) -> str:
        return '[{}]'.format(', '.join(map(str, self.defs)))

class Result:
    def __init__(self, msg : str, succeeded : bool):
        self.msg : str = msg
        self.__succeeded : bool = succeeded

    def succeeded(self) -> bool:
        return self.__succeeded

    def failed(self) -> bool:
        return not self.succeeded()

    def message(self) -> str:
        return self.msg

    def result_str(self) -> str:
        if settings.get_show_progress():
            if self.succeeded():
                return '{}{}{}'.format(Fore.GREEN, self.msg, Style.RESET_ALL)
            else:
                return '{}{}{}'.format(Fore.RED, self.msg, Style.RESET_ALL)
        else: # No colors
            return self.msg

class Restriction(IRNode):
    def __init__(self, restrict_vars : list[VarRef], pred : Call):
        super().__init__()
        self.restrict_vars : list[VarRef] = restrict_vars
        self.pred : Call = pred

    def evaluate(self, prog : Program) -> None:
        for var in self.restrict_vars:
            prog.global_restrict(var.var_name, self.pred.add_arg(var))

    def transform(self, transformer : IRTransformer) -> Restriction:
        return transformer.transform_Restriction(self)

    def __str__(self) -> str:
        if len(self.restrict_vars) == 1:
            return 'Restrict {} is {}.'.format(', '.join(map(str, self.restrict_vars)), self.pred)
        else:
            return 'Restrict {} are {}.'.format(', '.join(map(str, self.restrict_vars)), self.pred)
    
    def __repr__(self) -> str:
        return self.__str__()

class AutomatonStats(TypedDict):
    states : int
    edges : int
    runtime : float
