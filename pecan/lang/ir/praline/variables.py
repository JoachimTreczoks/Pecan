
from pecan.lang.ir.praline.base import PralineTerm, PralineDummy, PralineValueType
from pecan.tools.labeled_aut_converter import State, Transition, build_aut

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.automata.buchi import BuchiAutomaton
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.base import IRNode
    from pecan.lang.ir.prog import Program

class PralineValueHolder(PralineTerm):
    def __init__(self, value_type: PralineValueType):
        super().__init__(value_type)

class PralineVar(PralineValueHolder):
    def __init__(self, var_name : str):
        super().__init__('Variable')
        self.var_name : str = var_name

    def evaluate(self, prog : Program) -> PralineTerm:
        return prog.praline_lookup(self.var_name).evaluate(prog)

    def transform(self, transformer : IRTransformer) -> PralineVar:
        return transformer.transform_PralineVar(self)

    def __str__(self) -> str:
        return self.var_name
    
    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var_name == other.var_name

    def __hash__(self) -> int:
        return hash(self.var_name)

class PralineInt(PralineValueHolder):
    def __init__(self, val):
        super().__init__('int')
        self.val = val

    def transform(self, transformer : IRTransformer) -> PralineInt:
        return transformer.transform_PralineInt(self)

    def __str__(self) -> str:
        return '{}'.format(self.val)
    
    def __repr__(self) -> str:
        return 'PralineInt({})'.format(self.val)

    def evaluate(self, prog : Program) -> PralineInt:
        return self

    def get_int(self) -> int:
        return self.val

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)

class PralineString(PralineValueHolder):
    def __init__(self, val):
        super().__init__('string')
        self.val = val

    def transform(self, transformer : IRTransformer) -> PralineString:
        return transformer.transform_PralineString(self)

    def __str__(self) -> str:
        return self.val

    def __repr__(self) -> str:
        return 'PralineString({})'.format(self.val)

    def evaluate(self, prog : Program) -> PralineString:
        return self

    def get_string(self) -> str:
        return self.val

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)

class PralineBool(PralineValueHolder):
    def __init__(self, val):
        super().__init__('bool')
        self.val = val

    def transform(self, transformer : IRTransformer) -> PralineBool:
        return transformer.transform_PralineBool(self)

    def __str__(self) -> str:
        if self.val:
            return 'true'
        else:
            return 'false'

    def __repr__(self) -> str:
        return 'PralineBool({})'.format(self.val)

    def evaluate(self, prog : Program) -> PralineBool:
        return self

    def get_bool(self) -> bool:
        return self.val

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.val == other.val

    def __hash__(self) -> int:
        return hash(self.val)

class PralineTuple(PralineValueHolder):
    def __init__(self, vals : list[PralineTerm]):
        super().__init__('tuple')
        self.vals : list[PralineTerm] = vals

    def transform(self, transformer : IRTransformer) -> PralineTuple:
        return transformer.transform_PralineTuple(self)

    def __str__(self) -> str:
        return '({})'.format(', '.join(map(str, self.vals)))

    def __repr__(self) -> str:
        return '({})'.format(', '.join(map(repr, self.vals)))

    def evaluate(self, prog : Program) -> PralineTuple:
        return PralineTuple([v.evaluate(prog) for v in self.vals])

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.vals == other.vals

    def __hash__(self) -> int:
        return hash(self.vals)

class PralineList(PralineValueHolder):
    def __init__(self, head : None | PralineTerm, tail : None | PralineTerm):
        super().__init__('list')
        self.head : PralineTerm = head or PralineDummy()
        self.tail : PralineTerm = tail or PralineDummy()

        # Sanity check: self.tail is only non-trivial if self.head is non-trivial
        assert not (isinstance(self.head, PralineDummy) and not isinstance(self.tail, PralineDummy))

    def transform(self, transformer : IRTransformer) -> PralineList:
        return transformer.transform_PralineList(self)

    def __str__(self) -> str:
        elems = []
        cur : PralineList = self

        while not isinstance(cur.head, PralineDummy):
            elems.append(cur.head)
            if isinstance(cur.tail, PralineList):
                cur = cur.tail
            else:
                elems.append(cur.tail)
                break

        return '[{}]'.format(', '.join([str(e) for e in elems]))

    def __repr__(self) -> str:
        if isinstance(self.tail, PralineDummy):
            return '[]'
        else:
            return '({} :: {})'.format(self.head, self.tail)

    def evaluate(self, prog : Program) -> PralineList:
        if not isinstance(self.head, PralineDummy):
            new_a = self.head.evaluate(prog)
        else:
            new_a = None

        if not isinstance(self.tail, PralineDummy):
            new_b = self.tail.evaluate(prog)
        else:
            new_b = None

        return PralineList(new_a, new_b)
    
    def __eq__(self, other: Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.head == other.head and self.tail == other.tail

class PralinePecanLiteral(PralineValueHolder):
    def __init__(self, pecan_term : IRNode):
        super().__init__('PecanLiteral')
        self.pecan_term : IRNode = pecan_term

    def get_term(self) -> IRNode:
        return self.pecan_term

    def transform(self, transformer : IRTransformer) -> PralinePecanLiteral:
        return transformer.transform_PralinePecanLiteral(self)

    def evaluate(self, prog : Program) -> PralinePecanLiteral:
        return self

    def __str__(self) -> str:
        return '{{ {} }}'.format(self.pecan_term)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.pecan_term == other.pecan_term

    def __hash__(self) -> int:
        return hash((self.pecan_term))

class PralineAutomatonBuilder(PralineValueHolder):
    def __init__(self, input_names : list[str], input_bases : list[int], states : list[State], state_map : dict[str, int]):
        super().__init__('AutomatonBuilder')
        self.input_names : list[str] = input_names
        self.input_bases : list[int] = input_bases
        self.alphabet_line : str = ' '.join('{' + ', '.join(map(str, range(base))) + '}' for base in input_bases)

        self.states : list[State] = states
        self.state_map : dict[str, int] = state_map
        self.state_idx : int = len(self.states)

    def transform(self, transformer : IRTransformer) -> PralineAutomatonBuilder:
        return transformer.transform_PralineAutomatonBuilder(self)

    def __str__(self) -> str:
        return 'PralineAutomatonBuilder({}, {}, {}, {})'.format(self.input_names, self.input_bases, self.state_map, self.states)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.input_bases == other.input_bases and self.alphabet_line == other.alphabet_line and self.states == other.states and self.state_idx == other.state_idx and self.state_map == other.state_map and self.input_names == other.input_names

    def __hash__(self) -> int:
        return hash((self.alphabet_line, self.state_idx, len(self.states)))

    def evaluate(self, prog : Program) -> PralineAutomatonBuilder:
        return self

    def add_state(self, state_line : str) -> PralineAutomatonBuilder:
        new_state = State(self.state_idx, state_line)
        self.states.append(new_state)
        self.state_map[new_state.label] = self.state_idx

        self.state_idx += 1

        return self

    def add_transition(self, state_label : str, transition_line : str) -> PralineAutomatonBuilder:
        if state_label not in self.state_map:
            raise KeyError('No state "{}" in {}'.format(state_label, self))

        self.states[self.state_map[state_label]].add_transition(Transition(len(self.input_names), transition_line))

        return self

    def build(self) -> BuchiAutomaton:
        return build_aut(self.alphabet_line, self.states, self.state_map, self.input_names)
