#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Literal, Self, Iterable
    from pecan.lang.ir.prog import VarRef
    from pecan.utility import VarMap

class Automaton:
    def __init__(self, aut_type_name : str):
        self.aut_type_name = aut_type_name

    def get_aut_type(self) -> str:
        return self.aut_type_name

    # -------------------------------------------------------
    # Interface methods (should be implemented for all subclasses):
    # -------------------------------------------------------

    # To implement an automaton, we only need implement either conjunction or disjunction, and complement
    # In practice, it will probably be more efficient to implement all three
    def conjunction(self, other : Automaton) -> Automaton:
        """Returns an automaton representing the conjunction of this automaton and `other`"""
        return self.complement().disjunction(other.complement()).complement()

    def disjunction(self, other : Automaton) -> Automaton:
        """Returns an automaton representing the disjunction of this automaton and `other`"""
        return self.complement().conjunction(other.complement()).complement()

    def complement(self) -> Automaton:
        """Returns an automaton representing the complement of this automaton"""
        raise NotImplementedError

    def substitute(self, arg_map : dict[str, str], env_var_map : VarMap) -> Automaton:
        raise NotImplementedError

    def project(self, var_refs : Iterable[VarRef], env_var_map : VarMap) -> Automaton:
        raise NotImplementedError

    def is_empty(self) -> bool:
        raise NotImplementedError

    def truth_value(self) -> Literal['false', 'true', 'sometimes']:
        raise NotImplementedError

    def num_states(self) -> int:
        raise NotImplementedError

    def num_edges(self) -> int:
        raise NotImplementedError

    def accepting_word(self) -> dict | None:
        raise NotImplementedError

    def to_str(self) -> str:
        raise NotImplementedError

    # Should return a string of SVG data
    def __str__(self) -> str: # TODO: not literally str, check type
        raise NotImplementedError

    def save(self, filename : str) -> None:
        """Saves this automaton under the given filename"""
        raise NotImplementedError
    
    def get_var_map(self) -> VarMap:
        raise NotImplementedError

    # -------------------------------------------------------------------
    # Optional methods (e.g., for simplification, minimization, etc):
    # -------------------------------------------------------------------
    def simplify_edges(self) -> Automaton:
        return self

    def simplify_states(self) -> Automaton:
        return self

    def merge_edges(self) -> Automaton:
        return self

    def merge_states(self) -> Automaton:
        return self
    
    def postprocess(self, level : str | None = None) -> Self:
        return self

    # Allows conversion between types of automata, if desired
    def custom_convert(self, other : Automaton) -> Automaton:
        raise NotImplementedError

    def shuffle(self, is_disj : bool, other : Automaton) -> Automaton:
        raise NotImplementedError

    def relabel(self) -> Automaton:
        return self

    def simplify(self) -> Automaton:
        return self

    # -------------------------------------------------------
    # Default implementations:
    # -------------------------------------------------------
    def __and__(self, other : Automaton) -> Automaton:
        return self.conjunction(self.convert(other))

    def __or__(self, other : Automaton) -> Automaton:
        return self.disjunction(self.convert(other))

    def contains(self, other : Automaton) -> bool:
        return (self.complement() | other).truth_value() == 'true'

    def convert(self, other : Automaton) -> Automaton:
        if self.get_aut_type() == other.get_aut_type():
            return other
        else:
            return self.custom_convert(other)

class TrueAutomaton(Automaton):
    def __init__(self):
        super().__init__('true')

    def conjunction(self, other : Automaton) -> Automaton:
        return other

    def disjunction(self, other : Automaton) -> Automaton:
        return self

    def complement(self) -> Automaton:
        return FalseAutomaton()

    def substitute(self, arg_map : dict[str, str], env_var_map : VarMap) -> Automaton:
        return self

    def project(self, var_refs : Iterable[VarRef], env_var_map : VarMap) -> Automaton:
        return self

    def is_empty(self) -> bool:
        return False

    def truth_value(self) -> Literal['false', 'true', 'sometimes']:
        return 'true'

    def num_states(self) -> int:
        return -1

    def num_edges(self) -> int:
        return -1

    def custom_convert(self, other : Automaton) -> Automaton:
        return other

    def to_str(self) -> str:
        return str(self)

class FalseAutomaton(Automaton):
    def __init__(self):
        super().__init__('false')

    # We switch order so that we get converted into the proper automata type
    def conjunction(self, other : Automaton) -> Automaton:
        return self

    def disjunction(self, other : Automaton) -> Automaton:
        return other

    def complement(self) -> Automaton:
        return TrueAutomaton()

    def substitute(self, arg_map : dict[str, str], env_var_map : VarMap) -> Automaton:
        return self

    def project(self, var_refs : Iterable[VarRef], env_var_map : VarMap) -> Automaton:
        return self

    def is_empty(self) -> bool:
        return True

    def truth_value(self) -> Literal['false', 'true', 'sometimes']:
        return 'false'

    def num_states(self) -> int:
        return -1

    def num_edges(self) -> int:
        return -1

    def custom_convert(self, other : Automaton) -> Automaton:
        return other

    def to_str(self) -> str:
        return str(self)

