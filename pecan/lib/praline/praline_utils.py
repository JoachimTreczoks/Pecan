from pecan.lang.ir.praline.base import PralineTerm
from pecan.lang.ir.praline.variables import PralineValueHolder, PralineInt, PralineString, PralineBool, PralineTuple, PralineList, PralinePecanLiteral, PralineAutomatonBuilder
from pecan.exceptions import PralineTypeError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pecan.lang.ir.prog import Program

def lookup_term(var_name : str, prog : Program) -> PralineTerm:
    return prog.praline_lookup(var_name).evaluate(prog)

def lookup_value_holder(var_name : str, prog : Program) -> PralineValueHolder:
    value = lookup_term(var_name, prog)
    if isinstance(value, PralineValueHolder):
        return value
    else:
        raise PralineTypeError('Expected a PralineValueHolder, but got {} instead!'.format(type(value)))

def lookup_int(var_name : str, prog : Program) -> PralineInt:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralineInt):
        return value
    else:
        raise PralineTypeError('Expected an integer, but got {} instead!'.format(value.get_value_type()))
    
def lookup_string(var_name : str, prog : Program) -> PralineString:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralineString):
        return value
    else:
        raise PralineTypeError('Expected a string, but got {} instead!'.format(value.get_value_type()))
    
def lookup_bool(var_name : str, prog : Program) -> PralineBool:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralineBool):
        return value
    else:
        raise PralineTypeError('Expected a bool, but got {} instead!'.format(value.get_value_type()))
    
def lookup_tuple(var_name : str, prog : Program) -> PralineTuple:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralineTuple):
        return value
    else:
        raise PralineTypeError('Expected a tuple, but got {} instead!'.format(value.get_value_type()))

def lookup_list(var_name : str, prog : Program) -> PralineList:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralineList):
        return value
    else:
        raise PralineTypeError('Expected a list, but got {} instead!'.format(value.get_value_type()))

def lookup_pecan_literal(var_name : str, prog : Program) -> PralinePecanLiteral:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralinePecanLiteral):
        return value
    else:
        raise PralineTypeError('Expected a PecanLiteral, but got {} instead!'.format(value.get_value_type()))

def lookup_automaton(var_name : str, prog : Program) -> PralineAutomatonBuilder:
    value = lookup_value_holder(var_name, prog)
    if isinstance(value, PralineAutomatonBuilder):
        return value
    else:
        raise PralineTypeError('Expected an AutomatonBuilder, but got {} instead!'.format(value.get_value_type()))
