#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from functools import reduce

import pathlib

from pecan.lang.ir.praline import *
from pecan.lang.ir.base import IRPredicate
from pecan.lang.ir.prog import AutLiteral
from pecan.lib.plot import BuchiPlotter
from pecan.lib.praline.praline_utils import lookup_term, lookup_value_holder, lookup_int, lookup_string, lookup_bool, lookup_list, lookup_pecan_literal, lookup_automaton

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
        literal = lookup_pecan_literal('pecanTerm', prog)
        pecan_term = literal.get_term()

        if isinstance(pecan_term, IRPredicate):
            res = pecan_term.evaluate(prog)
            tval = res.truth_value()
            return PralineString(tval)
        else:
            raise PralineTypeError('Attempted computing truth value of a non-predicate Pecan term! Expected IRPredicate, but got {} instead.'.format(type(pecan_term)))

class ToString(Builtin):
    def __init__(self):
        super().__init__(PralineVar('toString'), [PralineVar('value')])

    def evaluate(self, prog : Program) -> PralineString:
        return PralineString(str(lookup_term('value', prog)))

class PralinePrint(Builtin):
    def __init__(self):
        super().__init__(PralineVar('print'), [PralineVar('string')])

    def evaluate(self, prog : Program) -> PralineBool:
        Logger.log(str(lookup_term('string', prog)))
        return PralineBool(True)

class Emit(Builtin):
    def __init__(self):
        super().__init__(PralineVar('emit'), [PralineVar('pecanTerm')])

    def evaluate(self, prog : Program) -> PralineBool:
        literal = lookup_pecan_literal('pecanTerm', prog)
        term = literal.get_term()

        Logger.debug('Emitted: "{}"'.format(term))
        prog.emit_definition(term)
        return PralineBool(True)

class FreshVar(Builtin):
    def __init__(self):
        super().__init__(PralineVar('freshVar'), [])

    def evaluate(self, prog : Program) -> PralineString:
        return PralineString(prog.fresh_name())

class ToChars(Builtin):
    def __init__(self):
        super().__init__(PralineVar('toChars'), [PralineVar('string')])

    def evaluate(self, prog : Program) -> PralineList:
        temp = lookup_string('string', prog)
        str_val = temp.get_string()

        result = PralineList(None, None)

        for c in str_val[::-1]:
            result = PralineList(PralineString(c), result)

        return result

class Cons(Builtin):
    def __init__(self):
        super().__init__(PralineVar('cons'), [PralineVar('head'), PralineVar('tail')])

    def evaluate(self, prog : Program) -> PralineList:
        return PralineList(lookup_term('head', prog), lookup_term('tail', prog))

class EnumFromTo(Builtin):
    def __init__(self):
        super().__init__(PralineVar('enumFromTo'), [PralineVar('low'), PralineVar('high')])

    def evaluate(self, prog : Program) -> PralineList:
        low = lookup_int('low', prog)
        high = lookup_int('high', prog)

        values = [i for i in range(low.get_int(), high.get_int() + 1)]
        result = PralineList(None, None)

        for value in values[::-1]:
            result = PralineList(PralineInt(value), result)

        return result

class AcceptingWord(Builtin):
    def __init__(self):
        super().__init__(PralineVar('acceptingWord'), [PralineVar('pecanTerm')])

    def evaluate(self, prog : Program) -> PralineList:
        literal = lookup_pecan_literal('pecanTerm', prog)
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

class Compare(Builtin):
    def __init__(self):
        super().__init__(PralineVar('compare'), [PralineVar('a'), PralineVar('b')])

    def evaluate(self, prog : Program) -> PralineInt:
        a = lookup_int('a', prog)
        b = lookup_int('b', prog)

        a_val = a.get_int()
        b_val = b.get_int()

        if a_val < b_val:
            return PralineInt(-1)
        elif a_val > b_val:
            return PralineInt(1)
        else:
            return PralineInt(0)

class Equal(Builtin):
    def __init__(self):
        super().__init__(PralineVar('equal'), [PralineVar('a'), PralineVar('b')])

    def evaluate(self, prog : Program) -> PralineBool:
        a_val = lookup_term('a', prog)
        b_val = lookup_term('b', prog)
        return PralineBool(a_val == b_val)


class MkAutomaton(Builtin):
    def __init__(self):
        super().__init__(PralineVar('mkAut'), [PralineVar('inputNames'), PralineVar('inputBases')])

    def evaluate(self, prog : Program) -> PralineAutomatonBuilder:
        input_names = as_python(lookup_list('inputNames', prog))
        input_bases = as_python(lookup_list('inputBases', prog))

        if isinstance(input_names, list) and isinstance(input_bases, list):
            return PralineAutomatonBuilder(input_names, input_bases, [], {})
        else:
            raise PralineTypeError('Attempted creating an automaton with non-list inputs! Expected PralineList, but got {} and {} instead.'.format(type(input_names), type(input_bases)))

class AddState(Builtin):
    def __init__(self):
        super().__init__(PralineVar('addState'), [PralineVar('automaton'), PralineVar('stateLabel'), PralineVar('isAccepting')])

    def evaluate(self, prog : Program) -> PralineAutomatonBuilder:
        aut = lookup_automaton('automaton', prog)
        label = lookup_string('stateLabel', prog)
        is_accepting = lookup_bool('isAccepting', prog)

        state_str = '{}: {}'.format(label.get_string(), 1 if is_accepting.get_bool() else 0)
        aut.add_state(state_str)

        return aut

class AddTransition(Builtin):
    def __init__(self):
        super().__init__(PralineVar('addTransition'), [PralineVar('automaton'), PralineVar('source'), PralineVar('destination'), PralineVar('acceptedValues')])

    def evaluate(self, prog : Program) -> PralineAutomatonBuilder:
        aut = lookup_automaton('automaton', prog)
        src = lookup_string('source', prog)
        dst = lookup_string('destination', prog)
        values = lookup_string('acceptedValues', prog)

        aut.add_transition(src.get_string(), '{} -> {}'.format(values.get_string(), dst.get_string()))
        return aut

class BuildAut(Builtin):
    def __init__(self):
        super().__init__(PralineVar('buildAut'), [PralineVar('automaton')])

    def evaluate(self, prog : Program) -> PralinePecanTerm:
        aut = lookup_automaton('automaton', prog)
        return PralinePecanTerm(AutLiteral(aut.build()))

class AutToStr(Builtin):
    def __init__(self):
        super().__init__(PralineVar('autToStr'), [PralineVar('automaton')])

    def evaluate(self, prog : Program) -> PralineString:
        literal = lookup_pecan_literal('automaton', prog)
        term = literal.get_term()

        if isinstance(term, AutLiteral):
            return PralineString(str(term.aut))
        else:
            raise PralineTypeError('Attempted turning an automaton into a string, but non-automaton Pecan term was given! Expected an AutLiteral, but got {} instead.'.format(term))

class WriteFile(Builtin):
    def __init__(self):
        super().__init__(PralineVar('writeFile'), [PralineVar('filepath'), PralineVar('string')])

    def evaluate(self, prog : Program) -> PralineBool:
        filepath = lookup_string('filepath', prog)
        contents = lookup_string('string', prog)

        with open(filepath.get_string(), 'w') as f:
            f.write(contents.get_string())

        prog.add_generated_file(filepath.get_string())

        return PralineBool(True)

class ReadFile(Builtin):
    def __init__(self):
        super().__init__(PralineVar('readFile'), [PralineVar('filepath')])

    def evaluate(self, prog : Program) -> PralineString:
        filepath = lookup_string('filepath', prog)

        with open(filepath.get_string(), 'r') as f:
            return PralineString(f.read())

class DeleteFile(Builtin):
    def __init__(self):
        super().__init__(PralineVar('deleteFile'), [PralineVar('filepath')])

    def evaluate(self, prog : Program) -> PralineBool:
        filepath = lookup_string('filepath', prog)

        pathlib.Path(filepath.get_string()).unlink()
        return PralineBool(True)

class Split(Builtin):
    def __init__(self):
        super().__init__(PralineVar('splitStr'), [PralineVar('separator'), PralineVar('string')])

    def evaluate(self, prog : Program):
        sep = lookup_string('separator', prog)
        input = lookup_string('string', prog)

        return as_praline(input.get_string().split(sep.get_string()))

class Plot(Builtin):
    def __init__(self):
        super().__init__(PralineVar('plot'), [PralineVar('options'), PralineVar('numerationSystems'), PralineVar('automaton')])

    def evaluate(self, prog : Program) -> PralineBool:
        options = as_python(lookup_list('options', prog))
        num_systems = as_python(lookup_list('numerationSystems', prog))
        literal = lookup_pecan_literal('automaton', prog)
        term = literal.get_term()

        if isinstance(term, IRPredicate):
            evaluation = term.evaluate(prog)
            Logger.info('Plotting {} using numeration systems {} with options: {}'.format(term, dict(num_systems), dict(options)))
            plotter = BuchiPlotter(prog, dict(num_systems), evaluation.aut, **dict(options))
            plotter.plot()
            return PralineBool(True)
        else:
            raise PralineTypeError('Attempted plotting an automaton, but non-predicate Pecan term was given! Expected IRPredicate, but got {} instead.'.format(type(term)))

class SetSettings(Builtin):
    def __init__(self):
        super().__init__(PralineVar('set'), [PralineVar('name'), PralineVar('value')])

    def evaluate(self, prog : Program) -> PralineBool:
        name = lookup_string('name', prog)
        value = as_python(lookup_value_holder('value', prog))

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

        if name.get_string() in settings_dict:
            settings_dict[name.get_string()](value)
        else:
            raise KeyError('Tried to set unknown setting {} to {}'.format(name.get_string(), value))

        return PralineBool(True)

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

