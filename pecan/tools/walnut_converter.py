#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import buddy
import math
import spot

from pecan.automata.buchi import BuchiAutomaton
from pecan.utility import VarMap

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Iterator

class Transition:
    def __init__(self, input_line : str):
        split = input_line.split('->')
        # Something like [1,2,3], representing a transition from (1,2,3) -> dest_state_name
        self.inputs : list[int] = [int(inp) for inp in split[0].split()]
        self.dest_state_name : int = int(split[1])

    # Suppose we have the following transition
    def encode(self, aut : BinaryAutomaton, hoa_aut : spot.twa_graph, state : State) -> spot.twa_graph:
        cond = buddy.bddtrue

        for encoded_input, aps in aut.encode(self.inputs):

            for c, ap in zip(encoded_input, aps):
                if c == '0':
                    cond &= -ap
                else:
                    cond &= ap

            acc_sets = aut.acc_for(self.dest_state_name)

        if acc_sets:
            hoa_aut.new_edge(state.state_num, aut.num_of(self.dest_state_name), cond, acc_sets)
        else:
            hoa_aut.new_edge(state.state_num, aut.num_of(self.dest_state_name), cond)

        return hoa_aut

class State:
    def __init__(self, state_num : int, acc : bool):
        self.state_num : int = state_num
        self.acc : bool = acc

        self.transitions : list[Transition] = []

    def add_transition(self, transition : Transition) -> None:
        self.transitions.append(transition)

    def encode_transitions(self, aut : BinaryAutomaton, hoa_aut : spot.twa_graph) -> spot.twa_graph:
        for transition in self.transitions:
            hoa_aut = transition.encode(aut, hoa_aut, self)

        return hoa_aut

    def get_acc(self) -> list[int]:
        return [0] if self.acc else []

def base_len(base):
    return math.ceil(math.log(base, 2))

class BinaryAutomaton:
    def __init__(self, input_alphabets : list[int], formal_arg_names : list[str]):
        self.input_alphabets : list[int] = input_alphabets
        self.formal_arg_names : list[str] = formal_arg_names

        if len(self.input_alphabets) != len(self.formal_arg_names):
            raise Exception('Number of inputs must match number of formal arguments ({} vs {})'.format(self.input_alphabets, self.formal_arg_names))

        self.states : list[State] = []
        self.state_num_map : dict[int, State] = {}
        self.state_name_map : dict[int, int] = {}

        self.state_num : int = 0

        self.hoa_aut : spot.twa_graph = spot.make_twa_graph()

        self.var_map : VarMap = VarMap()
        self.bdds : dict[str, list[buddy.bdd]] = {}
        for formal, base in zip(self.formal_arg_names, self.input_alphabets):
            self.var_map[formal] = [ BuchiAutomaton.fresh_ap() for _ in range(base_len(base)) ]
            self.bdds[formal] = [ buddy.bdd_ithvar(self.hoa_aut.register_ap(ap)) for ap in self.var_map[formal] ]

        self.hoa_aut.set_buchi()

    def add_state(self, line : str) -> State:
        split = line.split()
        state_name = int(split[0])
        acc = int(split[1]) == 1

        state_num = self.hoa_aut.new_state()

        # If it's the first state, it's going to be our initial state
        if not self.states:
            self.hoa_aut.set_init_state(state_num)

        new_state = State(state_num, acc)
        self.states.append(new_state)

        self.state_num_map[state_num] = new_state
        self.state_name_map[state_name] = state_num

        return new_state

    def encode(self, inp : list[int]) -> Iterator[tuple[str, buddy.bdd]]:
        for base, formal, sym in zip(self.input_alphabets, self.formal_arg_names, inp):
            yield bin(sym)[2:].rjust(base_len(base), '0'), self.bdds[formal]

    def acc_for(self, state_name : int) -> list[int]:
        return self.state_num_map[self.num_of(state_name)].get_acc()

    def num_of(self, state_name : int) -> int:
        return self.state_name_map[state_name]

    def to_buchi(self) -> BuchiAutomaton:
        for state in self.states:
            self.hoa_aut = state.encode_transitions(self, self.hoa_aut)

        return BuchiAutomaton(self.hoa_aut, self.var_map)

def parse_bases(line : str) -> list[int]:
    # TODO: Keep track of encoding along with variables and throw errors if variables are used wrong.
    bases = []

    split = [base_str.strip() for base_str in line.split('}') if base_str.strip() != '']

    for base_str in split:
        # Convert something like "{0,1,2}" into [0,1,2], then count how many places there are
        # TODO: Warn if base isn't all consecutive numbers.
        if base_str[0] == '{':
            base = len([int(part) for part in base_str[1:].split(',')])
            bases.append(base)
        else:
            raise Exception('Improperly formatted base string (expected it to be wrapped in "{{" and "}}"): "{}"'.format(base_str))

    return bases

def convert_aut(filename : str, input_names : list[str]) -> BuchiAutomaton:
    with open(filename, 'r') as f:
        return convert_walnut_lines(f.readlines(), input_names)

# TODO: It would be nice if we used a real parser for all this stuff
def convert_walnut_lines(lines : list[str], input_names : list[str]) -> BuchiAutomaton:
    cur_state = None
    aut = None

    bases = []

    for lineno, line in enumerate(lines):
        line = line.strip()

        if line == '':
            continue
        elif line[0] == '{':
            if aut is not None:
                raise Exception('Only one alphabet line is allowed!')

            # It's the alphabet line,
            bases = parse_bases(line)

            if len(bases) != len(input_names):
                raise Exception('Got {} input alphabets but {} formal arguments!'.format(len(bases), len(input_names)))

            aut = BinaryAutomaton(bases, input_names)
        elif '->' in line:
            if cur_state is None:
                raise Exception('Transition "{}" not inside any state! (line: {})'.format(line, lineno))
            cur_state.add_transition(Transition(line))
        elif len(line) > 1:
            if aut is None:
                raise Exception('Must declare the alphabet BEFORE declaring any states!')

            cur_state = aut.add_state(line)

    return aut.to_buchi()

