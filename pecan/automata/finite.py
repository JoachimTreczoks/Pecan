#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import itertools as it
from collections import deque
from typing import Literal

from pecan.automata.automaton import Automaton
from pecan.settings import settings

import PySimpleAutomata.NFA as NFA

# import foma.foma.python.foma as foma

class FiniteAutomaton(Automaton):
    """
    Model of finite automata

    Parameters
    ----------
    aut : dict
    var_map : dict

    Attributes
    ----------
    aut : dict
          The internal automaton representation
    var_map : dict
              A map (V \to (N x Sigma)) mapping variables to their index in the symbol and the alphabet of the symbol
    special_attr : Literal['false', 'true', None]
                   Whether the given automaton is the finite version of `TrueAutomaton`, `FalseAutomaton`, or neither
    """
    _id = 0
    @staticmethod
    def fresh_ap() -> str:
        """Returns a unique label to ensure unique automaton names."""
        label = f"__finvar{FiniteAutomaton._id}"
        FiniteAutomaton._id += 1
        return label

    @staticmethod
    def update_counter(ap_name : str) -> None:
        """
        This exists so that we ensure all names generated are fresh.
        It gets called by the various methods that may create an automaton which already uses of the reserved `__ap#N` names,
        such as loading an automaton from a file.

        Parameters
        ----------
        ap_name : str
                  Name of an automaton
        """
        if ap_name.startswith('var'):
            ap_num = int(ap_name.split('var')[1])
            FiniteAutomaton._id = max(FiniteAutomaton._id, ap_num) + 1

    @classmethod
    def as_finite(cls, aut : Automaton) -> FiniteAutomaton:
        """Turns automata into finite automata."""
        if aut.get_aut_type() == 'true':
            return cls.true_aut()
        elif aut.get_aut_type() == 'false':
            return cls.false_aut()
        else:
            raise NotImplementedError('No known conversion from {} to NFA.'.format(aut.get_aut_type()))

    def custom_convert(self, other : Automaton) -> FiniteAutomaton:
        """Redirects to FiniteAutomaton.as_finite()."""
        return FiniteAutomaton.as_finite(other)

    @classmethod
    def true_aut(cls) -> FiniteAutomaton:
        """Creates and returns a finite automaton that accepts anything."""
        f = FiniteAutomaton({
                'alphabet': set(),
                'states': set(),
                'initial_states': set(),
                'accepting_states': set(),
                'transitions': {}
            }, {})
        f.special_attr = 'true'
        return f

    @classmethod
    def false_aut(cls) -> FiniteAutomaton:
        """Creates and returns a finite automaton that accepts nothing."""
        f = FiniteAutomaton({
                'alphabet': set(),
                'states': set(),
                'initial_states': set(),
                'accepting_states': set(),
                'transitions': {}
            }, {})
        f.special_attr = 'false'
        return f

    def __init__(self, aut : dict, var_map : dict):
        super().__init__('finite')

        self.aut : dict = aut
        self.var_map : dict = var_map
        self.special_attr : Literal['false', 'true', None] = None

    def get_var_map(self) -> dict:
        return self.var_map

    def augment_vars(self, other : FiniteAutomaton) -> tuple[dict, dict, dict]:
        """Merges the variable maps of `self` and `other`.

        Parameters
        ----------
        other : FiniteAutomaton
                Other automaton to merge variable map with

        Returns
        -------
        new_l : dict
                Modified automaton based on `self` with the merged variable map, in NFA representation

        new_r : dict
                Modified automaton based on `other` with the merged variable map, in NFA representation

        new_var_map : dict
                      Merged variable map combining those of `self` and `other`
        """
        new_var_map = dict(self.var_map)
        cur_idx = len(new_var_map)

        for v, (idx, alphabet) in other.var_map.items():
            if v not in new_var_map:
                new_var_map[v] = (cur_idx, alphabet)
                cur_idx += 1

        new_l = self.with_var_map(new_var_map)
        new_r = other.with_var_map(new_var_map)

        return new_l, new_r, new_var_map

    def with_var_map(self, new_var_map : dict) -> dict:
        """Replaces the variable map of `self` with `new_var_map`.

        Parameters
        ----------
        new_var_map : dict
                      New variable map for `self`

        Returns
        -------
        FiniteAutomaton
                        Modified automaton based on `self` with the new variable map, in NFA representation
        """
        alphabets = list(range(len(new_var_map)))
        for v, (idx, alphabet) in new_var_map.items():
            alphabets[idx] = alphabet

        if len(alphabets) == 0:
            new_alphabet = set()
        else:
            new_alphabet = set(' '.join(symbol) for symbol in it.product(*alphabets))

        new_transitions = {}
        for (src, symbols), dsts in self.aut['transitions'].items():
            new_symbols = list(range(len(new_var_map)))

            # Copy over the old symbols
            symbols = symbols.split(' ')
            for v, (idx, alphabet) in self.var_map.items():
                # If a symbol isn't in the new map, just drop it
                if v in new_var_map:
                    new_symbols[new_var_map[v][0]] = [symbols[idx]]

            for v, (idx, alphabet) in new_var_map.items():
                if not v in self.var_map:
                    new_symbols[idx] = alphabet

            for new_symbol in it.product(*new_symbols):
                new_transitions[(src, ' '.join(new_symbol))] = dsts

        # Rename all states because PySimpleAutomata can't union automata with the same state names...
        # TODO: Probably very inefficient.
        return NFA.rename_nfa_states({
            'alphabet': new_alphabet,
            'states': self.aut['states'],
            'initial_states': self.aut['initial_states'],
            'accepting_states': self.aut['accepting_states'],
            'transitions': new_transitions
        }, FiniteAutomaton.fresh_ap())

    def conjunction(self, other : FiniteAutomaton) -> FiniteAutomaton:
        if self.special_attr == 'true' or other.special_attr == 'false':
            return other
        elif self.special_attr == 'false' or other.special_attr == 'true':
            return self
        else:
            aut_l, aut_r, new_var_map = self.augment_vars(other)
            return FiniteAutomaton(NFA.nfa_intersection(aut_l, aut_r), new_var_map)

    def disjunction(self, other : FiniteAutomaton) -> FiniteAutomaton:
        if self.special_attr == 'true' or other.special_attr == 'false':
            return self
        elif self.special_attr == 'false' or other.special_attr == 'true':
            return other
        else:
            aut_l, aut_r, new_var_map = self.augment_vars(other)
            return FiniteAutomaton(NFA.nfa_union(aut_l, aut_r), new_var_map)

    def complement(self) -> FiniteAutomaton:
        if self.special_attr == 'true':
            return FiniteAutomaton.false_aut()
        elif self.special_attr == 'false':
            return FiniteAutomaton.true_aut()
        else:
            # print('PERFORMING COMPLEMENT')
            # print(self.relabel_states().to_str())
            new_aut = NFA.nfa_complementation(self.aut)

            # Convert to an NFA
            new_aut['initial_states'] = {new_aut.pop('initial_state')}
            new_aut['transitions'] = {k: [v] for k, v in new_aut.pop('transitions').items()}

            res = FiniteAutomaton(new_aut, self.var_map)
            # print(res.relabel_states().to_str())
            return res

    def relabel(self) -> FiniteAutomaton:
        return self

    def substitute(self, arg_map : dict, env_var_map : dict) -> FiniteAutomaton:
        new_var_map = {}
        unified = {}

        for formal_arg, actual_arg in arg_map.items():
            # If we see repeats, only keep the first in the var map, but we need to keep track so we can adjust transitions appropriately later
            if actual_arg in new_var_map:
                unified[formal_arg] = new_var_map[actual_arg][0]
            else:
                new_var_map[actual_arg] = self.var_map[formal_arg]

        # Re-index the var map because we may have lost some variables to unification
        for i, v in enumerate(new_var_map.keys()):
            _, alphabet = new_var_map[v]
            new_var_map[v] = (i, alphabet)

        alphabets = list(range(len(new_var_map)))
        for v, (idx, alphabet) in new_var_map.items():
            alphabets[idx] = alphabet
        new_alphabet = set(' '.join(syms) for syms in it.product(*alphabets))

        new_transitions = {}
        for (src, sym), dsts in self.aut['transitions'].items():
            # Check if we should keep this transition, meaning that all positions
            # that were unified have the same letter for this transition
            new_sym = list(range(len(new_var_map)))
            keep = True

            syms = sym.split(' ')
            for v, (idx, alphabet) in self.var_map.items():
                # If a symbol isn't in the new map, just drop it
                if v in unified:
                    keep &= syms[idx] == syms[unified[v]]
                else:
                    # Copy over the symbol, using the new name of the variable
                    new_name = arg_map[v]
                    new_sym[new_var_map[new_name][0]] = syms[idx]

            if keep:
                new_transitions[(src, ' '.join(new_sym))] = dsts

        aut = {
            'alphabet': new_alphabet,
            'states': self.aut['states'],
            'initial_states': self.aut['initial_states'],
            'accepting_states': self.aut['accepting_states'],
            'transitions': new_transitions
        }

        return FiniteAutomaton(aut, new_var_map)

    def project(self, var_refs : set, env_var_map : dict) -> FiniteAutomaton:
        from pecan.lang.ir.prog import VarRef

        # print('Projecting', self.var_map, var_refs)
        # print(self.relabel_states().to_str())

        new_var_map = dict(self.var_map)
        for v in var_refs:
            # It may not be there (e.g., it's perfectly valid to do "exists x. y = y", even if it's pointless)
            if isinstance(v, VarRef) and v.var_name in new_var_map:
                popped_idx, _ = new_var_map.pop(v.var_name)

                # Shift down all indices of the new var map
                for new_v, (old_idx, alphabet) in new_var_map.items():
                    if old_idx > popped_idx:
                        new_var_map[new_v] = (old_idx - 1, alphabet)

        # If we've become empty, return one of the special false or true automata
        if len(new_var_map) == 0:
            if self.is_empty():
                return FiniteAutomaton.false_aut()
            else:
                return FiniteAutomaton.true_aut()
        else:
            new_aut = self.with_var_map(new_var_map)
            res = FiniteAutomaton(new_aut, new_var_map)
            # print(res.relabel_states().to_str())
            return res

    def is_empty(self) -> bool:
        if self.special_attr == 'true':
            return False
        elif self.special_attr == 'false':
            return True
        else:
            return not NFA.nfa_nonemptiness_check(self.aut)

    def truth_value(self) -> Literal['false', 'true', 'sometimes']:
        if self.is_empty(): # If we accept nothing, we are false
            return 'false'
        elif self.complement().is_empty(): # If our complement accepts nothing, we accept everything, so we are true
            return 'true'
        else: # Otherwise, we are neither true nor false: i.e., not all variables have been eliminated
            return 'sometimes'

    def relabel_states(self) -> FiniteAutomaton:
        """Changes state labels to be stringified integers in the range `[0, n)`, where `n` is the total number of states"""
        state_map = {}
        for i, s in enumerate(self.aut['states']):
            state_map[s] = str(i)

        new_initial_states = { state_map[s] for s in self.aut['initial_states'] }
        new_accepting_states = { state_map[s] for s in self.aut['accepting_states'] }
        new_transitions = { (state_map[src], sym): {state_map[dst] for dst in dsts} for (src, sym), dsts in self.aut['transitions'].items() }

        new_aut = {
            'alphabet': self.aut['alphabet'],
            'states': set(state_map.values()),
            'initial_states': new_initial_states,
            'accepting_states': new_accepting_states,
            'transitions': new_transitions
        }

        return FiniteAutomaton(new_aut, self.var_map)

    def accepting_word(self) -> dict | None:
        # mostly copied from PySimpleAutomata's emptiness checking code

        # BFS
        symbol_history = {}

        queue = deque()
        visited = set()
        for state in self.aut['initial_states']:
            visited.add(state)
            queue.append(state)

        final_state = None
        while queue:
            state = queue.popleft()
            visited.add(state)
            for a in self.aut['alphabet']:
                if (state, a) in self.aut['transitions']:
                    for next_state in self.aut['transitions'][state, a]:
                        # keep track of where we've been
                        if next_state in self.aut['accepting_states']:
                            symbol_history[next_state] = (state, a)
                            final_state = next_state
                            break
                        if next_state not in visited:
                            symbol_history[next_state] = (state, a)
                            queue.append(next_state)

        if final_state is not None:
            res = []
            while not final_state in self.aut['initial_states']:
                final_state, next_sym = symbol_history[final_state]
                # print(final_state, ':', next_sym)
                res.append(next_sym)

            var_order = list(range(len(self.var_map)))
            for v, (idx, alphabet) in self.var_map.items():
                var_order[idx] = v
            return { ' '.join(var_order): res[::-1] }

        return None

    def num_states(self) -> int:
        return len(self.aut['states'])

    def num_edges(self) -> int:
        return len(self.aut['transitions'])

    # Should return a string of SVG data
    def show(self) -> str:
        return str(self.aut)

    def get_aut(self) -> dict:
        return self.aut

    def to_str(self) -> str:
        return '{}'.format({'var_map': self.var_map, 'special_attr': self.special_attr, 'aut': self.aut})

    def save(self, filename : str) -> None:
        with open(filename, 'w') as f:
            f.write(self.to_str())

