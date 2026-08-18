#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from functools import reduce

import pathlib

from pecan.lang.ir.praline import *
from pecan.lang.ir.base import IRPredicate
from pecan.lang.ir.prog import AutLiteral
from pecan.lib.plot import BuchiPlotter

from pecan.settings import settings
from pecan.logger import Logger
from pecan.exceptions import PralineConversionError, PralineTypeError

def as_praline(val : list | str | bool | int | tuple) -> PralineList | PralineString | PralineBool | PralineInt | PralineTuple:
    if isinstance(val, list):
        result = PralineList(None, None)

        for v in val[::-1]:
            result = PralineList(as_praline(v), result)

        return result
    elif isinstance(val, str):
        return PralineString(val)
    elif isinstance(val, bool):
        return PralineBool(val)
    elif isinstance(val, int):
        return PralineInt(val)
    elif isinstance(val, tuple):
        return PralineTuple([as_praline(v) for v in val])
    else:
        raise PralineConversionError("Can't convert {} ({}) to a Praline value".format(type(val), val))

def as_python(val, expected = None) -> list | str | bool | int | tuple | IRNode:
    if isinstance(val, PralineList):
        if expected is None or isinstance(val, expected):
            result = []
            while not isinstance(val.head, PralineDummy):
                result.append(as_python(val.head))
                if isinstance(val.tail, PralineList):
                    val = val.tail
                else:
                    result.append(as_python(val.tail))
                    break

            return result
    elif isinstance(val, PralineString):
        if expected is None or isinstance(val, expected):
            return val.val
    elif isinstance(val, PralineBool):
        if expected is None or isinstance(val, expected):
            return val.val
    elif isinstance(val, PralineInt):
        if expected is None or isinstance(val, expected):
            return val.val
    elif isinstance(val, PralineTuple):
        if expected is None or isinstance(val, expected):
            return tuple([as_python(v) for v in val.vals])
    # Currently, this is **only** for unwrapping automata
    elif isinstance(val, PralinePecanLiteral):
        if expected is None or isinstance(val, expected):
            return val.get_term()
    else:
        raise PralineConversionError("Can't convert {} ({}) to a Python value".format(type(val), val))

    if expected is not None:
        raise PralineTypeError('Expected type was {}, but got value: {}'.format(expected, val))
    else:
        raise PralineConversionError('Unexpected error while converting {} to a Python value (expected type: {})'.format(val, expected))

class TruthValue(Builtin):
    def __init__(self):
        super().__init__(PralineVar('truthValue'), [PralineVar('pecanTerm')])

    def evaluate(self, prog : Program) -> PralineString:
        literal = prog.praline_lookup('pecanTerm').evaluate(prog)

        if isinstance(literal, PralinePecanLiteral):
            pecan_term = literal.get_term()

            if isinstance(pecan_term, IRPredicate):
                res = pecan_term.evaluate(prog)
                tval = res.truth_value()
                return PralineString(tval)
            else:
                raise PralineTypeError('Attempted computing truth value of a non-predicate Pecan term! Expected IRPredicate, but got {} instead.'.format(type(pecan_node)))
        else:
          raise PralineTypeError('Attempted computing truth value of a non-Pecan term! Expected IRPredicate, but got {} instead.'.format(type(term)))

class ToString(Builtin):
    def __init__(self):
        super().__init__(PralineVar('toString'), [PralineVar('value')])

    def evaluate(self, prog : Program) -> PralineString:
        t = prog.praline_lookup('value').evaluate(prog)

        return PralineString(str(t))

class PralinePrint(Builtin):
    def __init__(self):
        super().__init__(PralineVar('print'), [PralineVar('string')])

    def evaluate(self, prog : Program) -> PralineBool:
        Logger.log(str(prog.praline_lookup('string').evaluate(prog)))
        return PralineBool(True)

class Emit(Builtin):
    def __init__(self):
        super().__init__(PralineVar('emit'), [PralineVar('pecanTerm')])

    def evaluate(self, prog : Program) -> PralineBool:
        literal = prog.praline_lookup('pecanTerm').evaluate(prog)
        if isinstance(literal, PralinePecanLiteral):
            term = literal.get_term()
            Logger.debug('Emitted: "{}"'.format(term))
            prog.emit_definition(term)
            return PralineBool(True)
        else:
            raise PralineTypeError('Attempted emitting a non-Pecan term! Expected PralinePecanLiteral, but got {} instead.'.format(type(literal)))

class FreshVar(Builtin):
    def __init__(self):
        super().__init__(PralineVar('freshVar'), [])

    def evaluate(self, prog : Program) -> PralineString:
        return PralineString(prog.fresh_name())

class ToChars(Builtin):
    def __init__(self):
        super().__init__(PralineVar('toChars'), [PralineVar('string')])

    def evaluate(self, prog : Program) -> PralineList:
        temp = prog.praline_lookup('string').evaluate(prog)
        if isinstance(temp, PralineString):
            str_val = temp.get_string()

            result = PralineList(None, None)

            for c in str_val[::-1]:
                result = PralineList(PralineString(c), result)

            return result
        else:
            raise PralineTypeError('Attempted splitting a non-string! Expected PralineString, but got {} instead.'.format(type(temp)))

class Cons(Builtin):
    def __init__(self):
        super().__init__(PralineVar('cons'), [PralineVar('head'), PralineVar('tail')])

    def evaluate(self, prog : Program) -> PralineList:
        return PralineList(prog.praline_lookup('head').evaluate(prog), prog.praline_lookup('tail').evaluate(prog))

class AcceptingWord(Builtin):
    def __init__(self):
        super().__init__(PralineVar('acceptingWord'), [PralineVar('pecanTerm')])

    def evaluate(self, prog : Program) -> PralineList:
        literal = prog.praline_lookup('pecanTerm').evaluate(prog)

        if isinstance(literal, PralinePecanLiteral):
            pecan_term = literal.get_term()

            if isinstance(pecan_term, IRPredicate):
                res = pecan_term.evaluate(prog)
                acc_word = res.accepting_word()

                result = PralineList(None, None)
                for var_name, vs in acc_word.items():
                    result = PralineList(PralineTuple([PralineString(var_name), as_praline(vs)]), result)

                return result
            else:
                raise PralineTypeError('Attempted computing accepted words of a non-predicate Pecan term! Expected IRPredicate, but got {} instead.'.format(type(pecan_term)))
        else:
          raise PralineTypeError('Attempted computing accepted words of a non-Pecan term! Expected IRPredicate, but got {} instead.'.format(type(literal)))

class Compare(Builtin):
    def __init__(self):
        super().__init__(PralineVar('compare'), [PralineVar('a'), PralineVar('b')])

    def evaluate(self, prog : Program) -> PralineInt:
        a = prog.praline_lookup('a').evaluate(prog)
        b = prog.praline_lookup('b').evaluate(prog)

        if isinstance(a, PralineInt) and isinstance(b, PralineInt):
            a_val = a.get_int()
            b_val = b.get_int()

            if a_val < b_val:
                return PralineInt(-1)
            elif a_val > b_val:
                return PralineInt(1)
            else:
                return PralineInt(0)
        else:
            raise PralineTypeError('Attempted comparing non-integer values! Expected PralineInt, but got {} and {} instead.'.format(type(a), type(b)))

class Equal(Builtin):
    def __init__(self):
        super().__init__(PralineVar('equal'), [PralineVar('a'), PralineVar('b')])

    def evaluate(self, prog : Program) -> PralineBool:
        a_val = prog.praline_lookup('a').evaluate(prog)
        b_val = prog.praline_lookup('b').evaluate(prog)
        return PralineBool(a_val == b_val)


class MkAutomaton(Builtin):
    def __init__(self):
        super().__init__(PralineVar('mkAut'), [PralineVar('inputNames'), PralineVar('inputBases')])

    def evaluate(self, prog : Program) -> PralineAutomaton:
        input_names = as_python(prog.praline_lookup('inputNames').evaluate(prog))
        input_bases = as_python(prog.praline_lookup('inputBases').evaluate(prog))

        if isinstance(input_names, list) and isinstance(input_bases, list):
            return PralineAutomaton(input_names, input_bases, [], {})
        else:
            raise PralineTypeError('Attempted creating an automaton with non-list inputs! Expected PralineList, but got {} and {} instead.'.format(type(input_names), type(input_bases)))

class AddState(Builtin):
    def __init__(self):
        super().__init__(PralineVar('addState'), [PralineVar('automaton'), PralineVar('stateLabel'), PralineVar('isAccepting')])

    def evaluate(self, prog : Program) -> PralineAutomaton:
        aut = prog.praline_lookup('automaton').evaluate(prog)

        if isinstance(aut, PralineAutomaton):
            label = prog.praline_lookup('stateLabel').evaluate(prog)

            if isinstance(label, PralineString):
                is_accepting = prog.praline_lookup('isAccepting').evaluate(prog)

                if isinstance(is_accepting, PralineBool):
                    state_str = '{}: {}'.format(label.get_string(), 1 if is_accepting.get_bool() else 0)
                    aut.add_state(state_str)

                    return aut
                else:
                    raise PralineTypeError('Attempted adding state, but non-boolean acceptance was given! Expected PralineBool, but got {} instead.'.format(type(isAccepting)))
            else:
                raise PralineTypeError('Attempted adding state, but non-string state name was given! Expected PralineString, but got {} instead.'.format(type(label)))
        else:
            raise PralineTypeError('Attempted adding state, but non-automaton was given! Expected PralineAutomaton, but got {} instead.'.format(type(aut)))

class AddTransition(Builtin):
    def __init__(self):
        super().__init__(PralineVar('addTransition'), [PralineVar('automaton'), PralineVar('source'), PralineVar('destination'), PralineVar('acceptedValues')])

    def evaluate(self, prog : Program) -> PralineAutomaton:
        aut = prog.praline_lookup('automaton').evaluate(prog)

        if isinstance(aut, PralineAutomaton):
            src = prog.praline_lookup('source').evaluate(prog)

            if isinstance(src, PralineString):
                dst = prog.praline_lookup('destination').evaluate(prog)

                if isinstance(dst, PralineString):
                    values = prog.praline_lookup('acceptedValues').evaluate(prog)

                    if isinstance(values, PralineString):
                        aut.add_transition(src.get_string(), '{} -> {}'.format(values.get_string(), dst.get_string()))
                        return aut
                    else:
                        raise PralineTypeError('Attempted adding transition, but non-string accepted values were given! Expected PralineString, but got {} instead.'.format(type(syms)))
                else:
                    raise PralineTypeError('Attempted adding transition, but non-string destination was given! Expected PralineString, but got {} instead.'.format(type(dst)))
            else:
                raise PralineTypeError('Attempted adding transition, but non-string source was given! Expected PralineString, but got {} instead.'.format(type(src)))
        else:
            raise PralineTypeError('Attempted adding transition, but non-automaton was given! Expected PralineAutomaton, but got {} instead.'.format(type(aut)))

                        

class BuildAut(Builtin):
    def __init__(self):
        super().__init__(PralineVar('buildAut'), [PralineVar('automaton')])

    def evaluate(self, prog : Program) -> PralinePecanTerm:
        aut = prog.praline_lookup('automaton').evaluate(prog)
        if isinstance(aut, PralineAutomaton):
            return PralinePecanTerm(AutLiteral(aut.build()))
        else:
            raise PralineTypeError('Attempted building automaton, but non-automaton was given! Expected PralineAutomaton, but got {} instead.'.format(type(aut)))

class AutToStr(Builtin):
    def __init__(self):
        super().__init__(PralineVar('autToStr'), [PralineVar('automaton')])

    def evaluate(self, prog : Program) -> PralineString:
        literal = prog.praline_lookup('automaton').evaluate(prog)
        if isinstance(literal, PralinePecanLiteral):
            term = literal.get_term()
            if isinstance(term, AutLiteral):
                return PralineString(str(term.aut))
            else:
                raise PralineTypeError('Attempted turning an automaton to a string, but non-automaton was given! Expected an AutLiteral, but got {} instead.'.format(term))
        else:
            raise PralineTypeError('Attempted turning an automaton to a string, but non-automaton was given! Expected a PralinePecanLiteral, but got {} instead.'.format(literal))

class WriteFile(Builtin):
    def __init__(self):
        super().__init__(PralineVar('writeFile'), [PralineVar('filepath'), PralineVar('string')])

    def evaluate(self, prog : Program) -> PralineBool:
        filepath = prog.praline_lookup('filepath').evaluate(prog)

        if isinstance(filepath, PralineString):
            contents = prog.praline_lookup('string').evaluate(prog)

            if isinstance(contents, PralineString):
                with open(filepath.get_string(), 'w') as f:
                    f.write(contents.get_string())

                prog.add_generated_file(filepath.get_string())

                return PralineBool(True)
            else:
                raise PralineTypeError('Attempted writing to a file, but non-string contents were given! Expected PralineString, but got {} instead.'.format(type(contents)))
        else:
            raise PralineTypeError('Attempted writing to a file, but non-string filepath was given! Expected PralineString, but got {} instead.'.format(type(filepath)))

class ReadFile(Builtin):
    def __init__(self):
        super().__init__(PralineVar('readFile'), [PralineVar('filepath')])

    def evaluate(self, prog : Program) -> PralineString:
        filepath = prog.praline_lookup('filepath').evaluate(prog)

        if isinstance(filepath, PralineString):
            with open(filepath.get_string(), 'r') as f:
                return PralineString(f.read())
        else:
            raise PralineTypeError('Attempted reading a file, but non-string filepath was given! Expected PralineString, but got {} instead.'.format(type(filepath)))

class DeleteFile(Builtin):
    def __init__(self):
        super().__init__(PralineVar('deleteFile'), [PralineVar('filepath')])

    def evaluate(self, prog : Program) -> PralineBool:
        filepath = prog.praline_lookup('filepath').evaluate(prog)

        if isinstance(filepath, PralineString):
            pathlib.Path(filepath.get_string()).unlink()
            return PralineBool(True)
        else:
            raise PralineTypeError('Attempted deleting a file, but non-string filepath was given! Expected PralineString, but got {} instead.'.format(type(filepath)))

class Split(Builtin):
    def __init__(self):
        super().__init__(PralineVar('splitStr'), [PralineVar('separator'), PralineVar('string')])

    def evaluate(self, prog : Program):
        sep = prog.praline_lookup('seperator').evaluate(prog)

        if isinstance(sep, PralineString):
            input = prog.praline_lookup('string').evaluate(prog)

            if isinstance(input, PralineString):
                return as_praline(input.get_string().split(sep.get_string()))
            else:
                raise PralineTypeError('Attempted splitting a string, but non-string input was given! Expected PralineString, but got {} instead.'.format(type(input)))
        else:
            raise PralineTypeError('Attempted splitting a string, but non-string separator was given! Expected PralineString, but got {} instead.'.format(type(sep)))

class Plot(Builtin):
    def __init__(self):
        super().__init__(PralineVar('plot'), [PralineVar('options'), PralineVar('numerationSystems'), PralineVar('automaton')])

    def evaluate(self, prog : Program) -> PralineBool:
        options = as_python(prog.praline_lookup('options').evaluate(prog))

        if isinstance(options, list):
            num_systems = as_python(prog.praline_lookup('numerationSystems').evaluate(prog))

            if isinstance(num_systems, list):
                term = as_python(prog.praline_lookup('automaton').evaluate(prog), PralinePecanLiteral)

                if isinstance(term, IRPredicate):
                    evaluation = term.evaluate(prog)
                    Logger.info('Plotting {} using numeration systems {} with options: {}'.format(term, dict(num_systems), dict(options)))
                    plotter = BuchiPlotter(prog, dict(num_systems), evaluation.aut, **dict(options))
                    plotter.plot()
                    return PralineBool(True)
                else:
                    raise PralineTypeError('Attempted plotting an automaton, but non-predicate Pecan term was given! Expected IRPredicate, but got {} instead.'.format(type(term)))
            else:
                raise PralineTypeError('Attempted splitting a string, but non-list numeration systems were given! Expected PralineList, but got {} instead.'.format(type(as_praline(num_systems))))
        else:
            raise PralineTypeError('Attempted splitting a string, but non-list options were given! Expected PralineList, but got {} instead.'.format(type(as_praline(options))))

class SetSettings(Builtin):
    def __init__(self):
        super().__init__(PralineVar('set'), [PralineVar('name'), PralineVar('value')])

    def evaluate(self, prog : Program) -> PralineBool:
        name = as_python(prog.praline_lookup('name').evaluate(prog), PralineString)
        if isinstance(name, str):
            value = as_python(prog.praline_lookup('value').evaluate(prog))

            settings_dict = {
                'output_json': settings.set_output_json,
                'show_progress': settings.set_show_progress,
                'write_statistics': settings.set_write_statistics,
                'extract_implications': settings.set_extract_implications,
                'min_opt': settings.set_min_opt,
                'simplification_level': settings.set_simplification_level,
                'history_file': settings.set_history_file,
                'debug_level': settings.set_debug_level,
                'quiet': settings.set_quiet,
                'opt_level': settings.set_opt_level,
                'heuristics': settings.set_use_heuristics,
                'postprocessing_preference': settings.set_postprocessing_preference,
                'postprocessing_force_sbacc': settings.set_postprocessing_force_sbacc,
                'load_stdlib': settings.set_load_stdlib,
                'output_hoa': settings.set_output_hoa,
            }

            if name in settings_dict:
                settings_dict[name](value)
            else:
                raise KeyError('Tried to set unknown setting {} to {}'.format(name, value))

            return PralineBool(True)
        else:
            raise PralineTypeError('Attempted changing a setting, but non-string setting name was given! Expected PralineString, but got {} instead.'.format(type(as_praline(name))))

builtins = [
    TruthValue().definition(),
    ToString().definition(),
    Split().definition(),
    PralinePrint().definition(),
    Emit().definition(),
    FreshVar().definition(),
    AcceptingWord().definition(),
    ToChars().definition(),
    Cons().definition(),
    EnumFromTo().definition(),
    Compare().definition(),
    Equal().definition(),
    MkAutomaton().definition(),
    AddState().definition(),
    AddTransition().definition(),
    BuildAut().definition(),
    AutToStr().definition(),
    DeleteFile().definition(),
    WriteFile().definition(),
    ReadFile().definition(),
    Plot().definition(),
    SetSettings().definition(),
]

