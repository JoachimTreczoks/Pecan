#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.tools.walnut_converter import convert_walnut_lines
from pecan.automata.buchi import BuchiAutomaton

class Transition:
    def __init__(self, input_size : int, input_line : str):
        split : list[str] = input_line.split('->')
        self.inputs : list[str] = [inp.strip() for inp in split[0].split()]
        self.dest_label : str = split[1].strip()

        if len(self.inputs) != input_size:
            raise Exception('Expected {} input symbols for transition, only got {} in "{}"'.format(input_size, len(self.inputs), input_line))

    def to_str(self, state_map : dict[str, int]) -> str:
        return '{} -> {}'.format(self.input_str(), state_map[self.dest_label])

    def input_str(self) -> str:
        return ' '.join(self.inputs)

    def __str__(self) -> str:
        return 'Transition({}, {})'.format(self.inputs, self.dest_label)

class State:
    def __init__(self, idx : int, input_line : str):
        self.idx : int = idx

        split : list[str] = input_line.split(':')
        self.label : str = split[0].strip()
        self.acc : bool = int(split[1]) == 1

        self.transitions : list[Transition] = []

    def add_transition(self, transition : Transition) -> None:
        self.transitions.append(transition)

    def to_str(self, state_map : dict[str, int]) -> list[str]:
        lines = []
        lines.append('{} {}'.format(self.idx, 1 if self.acc else 0))
        for transition in self.transitions:
            lines.append(transition.to_str(state_map))
        return lines

    def __str__(self) -> str:
        return 'State({}, {}, {})'.format(self.label, self.acc, self.transitions)

# TODO: It would be nice if we used a real parser for all this stuff
def convert_labeled_aut(filename : str, input_names : list[str]) -> BuchiAutomaton:
    state_idx = 0
    cur_state = None

    state_map = {}
    states = []

    alphabet_line = None

    with open(filename, 'r') as f:
        for lineno, line in enumerate(f.readlines()):
            line = line.strip()

            if line.startswith('//') or len(line) <= 0:
                pass
            elif line[0] == '{':
                # It's the alphabet line,
                alphabet_line = line
            elif '->' in line:
                if cur_state is None:
                    raise Exception('Transition "{}" not inside any state! (line: {})'.format(line, lineno))
                cur_state.add_transition(Transition(len(input_names), line))
            elif len(line) > 1:
                cur_state = State(state_idx, line)
                state_map[cur_state.label] = state_idx
                states.append(cur_state)
                state_idx += 1

    return build_aut(alphabet_line, states, state_map, input_names)

def build_aut(alphabet_line : str, states : list[State], state_map : dict[str, int], input_names : list[str]) -> BuchiAutomaton:
    lines = [alphabet_line]

    for state in states:
        lines.extend(state.to_str(state_map))

    return convert_walnut_lines(lines, input_names)

