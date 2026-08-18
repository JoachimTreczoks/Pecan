
from pecan.lang.ir.praline.base import PralineIRNode, PralineTerm, PralineDummy
from pecan.tools.labeled_aut_converter import *


from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.base import IRNode
    from pecan.lang.ir.prog import Program
    from pecan.lang.ir.praline.variables import PralineVar

class PralineAlias(PralineIRNode):
    def __init__(self, name : str, directive_name : str, term : PralineApp | PralineVar):
        super().__init__()
        self.name : str = name
        self.directive_name : str = directive_name
        self.term : PralineApp | PralineVar = term

    def evaluate(self, prog : Program) -> PralineDummy:
        prog.define_alias(self.name, self)
        return PralineDummy()

    def with_term(self, new_term : PralineTerm) -> PralineDirective:
        return PralineDirective(self.directive_name, PralineApp(self.term, new_term))

    def transform(self, transformer : IRTransformer) -> PralineAlias:
        return transformer.transform_PralineAlias(self)

    def __str__(self) -> str:
        return 'Alias "{}" ==> {} {} .'.format(self.name, self.directive_name, self.term)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.name == other.name and self.directive_name == other.directive_name and self.term == other.term

    def __hash__(self) -> int:
        return hash((self.name, self.directive_name, self.term))

class PralineDirective(PralineIRNode):
    def __init__(self, name : str, term : PralineTerm):
        super().__init__()
        self.name : str = name
        self.term : PralineTerm = term

    def evaluate(self, prog : Program) -> PralineTerm:
        if self.name == 'Execute':
            prog.enter_praline_env()
            self.term.evaluate(prog)
            prog.exit_praline_env()
            return PralineDummy()
        else:
            return prog.lookup_alias(self.name).with_term(self.term).evaluate(prog)

    def transform(self, transformer : IRTransformer) -> PralineDirective:
        return transformer.transform_PralineDirective(self)

    def __str__(self) -> str:
        return '{} {} .'.format(self.name, self.term)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.name == other.name and self.term == other.term

    def __hash__(self) -> int:
        return hash((self.name, self.term))

class PralineDef(PralineIRNode):
    def __init__(self, name : PralineVar, args : list[PralineVar], body : PralineTerm):
        super().__init__()
        self.name : PralineVar = name
        self.args : list[PralineVar] = args
        self.body : PralineTerm = body

    def evaluate(self, prog : Program) -> PralineDummy:
        res = Closure({}, self.args, self.body)
        prog.praline_define(self.name.var_name, res)
        return PralineDummy()

    def transform(self, transformer : IRTransformer) -> PralineDef:
        return transformer.transform_PralineDef(self)

    def __str__(self) -> str:
        return 'Define {} {} := {} .'.format(self.name, self.args, self.body)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.name == other.name and self.args == other.args and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.name, self.args, self.body))


class PralineApp(PralineTerm):
    def __init__(self, receiver : PralineApp | PralineVar, arg : PralineTerm):
        super().__init__()
        self.receiver : PralineApp | PralineVar = receiver
        self.arg : PralineTerm = arg

    def evaluate(self, prog : Program) -> PralineTerm:
        evaluation = self.receiver.evaluate(prog)
        if isinstance(evaluation, Closure):
            return evaluation.apply(prog, self.arg.evaluate(prog)).evaluate(prog)
        else:
            raise TypeError('Expected {} to evaluate to Closure, but got {} instead'.format(self.receiver, type(evaluation)))

    def transform(self, transformer : IRTransformer) -> PralineApp:
        return transformer.transform_PralineApp(self)

    def __str__(self) -> str:
        return '({} {})'.format(self.receiver, self.arg)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.receiver == other.receiver and self.arg == other.arg

    def __hash__(self) -> int:
        return hash((self.receiver, self.arg))

class PralinePecanLiteral(PralineTerm):
    def __init__(self, pecan_term : IRNode):
        super().__init__()
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

class PralinePecanTerm(PralineTerm):
    def __init__(self, pecan_term : IRNode):
        super().__init__()
        self.pecan_term : IRNode = pecan_term

    def transform(self, transformer : IRTransformer) -> PralinePecanTerm:
        return transformer.transform_PralinePecanTerm(self)

    def __str__(self) -> str:
        return '{{ {} }}'.format(self.pecan_term)

    def evaluate(self, prog : Program) -> PralinePecanLiteral:
        from pecan.lang.ir_substitution import IRSubstitution
        from pecan.lang.praline_to_pecan import PralineToPecan

        temp_node = PralineToPecan().transform(IRSubstitution(prog.praline_env_clone()).transform(self.pecan_term))

        from pecan.lang.typed_ir_lowering import TypedIRLowering
        new_node = TypedIRLowering(prog).transform(prog.type_infer(temp_node))
        return PralinePecanLiteral(new_node)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.pecan_term == other.pecan_term

    def __hash__(self) -> int:
        return hash((self.pecan_term))

class PralineLambda(PralineTerm):
    def __init__(self, params : list[PralineVar], body : PralineTerm):
        super().__init__()
        self.params : list[PralineVar] = params
        self.body : PralineTerm = body

    def transform(self, transformer : IRTransformer) -> PralineLambda:
        return transformer.transform_PralineLambda(self)

    def __str__(self) -> str:
        return '(\\ {} -> {})'.format(self.params, self.body)

    def evaluate(self, prog : Program) -> Closure:
        return Closure(prog.praline_env_clone(), self.params, self.body)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.params == other.params and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.params, self.body))

class PralineLetPecan(PralineTerm):
    def __init__(self, var_name : str, pecan_term : PralinePecanTerm, body : PralineTerm):
        super().__init__()
        self.var_name : str = var_name
        self.pecan_term : PralinePecanTerm = pecan_term
        self.body : PralineTerm = body

    def transform(self, transformer : IRTransformer) -> PralineLetPecan:
        return transformer.transform_PralineLetPecan(self)

    def __str__(self) -> str:
        return '(let {} be {} in {})'.format(self.var_name, self.pecan_term, self.body)

    def evaluate(self, prog : Program) -> PralineTerm:
        result_node = self.pecan_term.evaluate(prog).evaluate(prog).pecan_term

        from pecan.lang.ir.prog import AutLiteral, VarRef
        from pecan.lang.ir.arith import PredicateExpr
        expr = PredicateExpr(VarRef(self.var_name), AutLiteral(result_node.evaluate(prog).aut))
        prog.praline_local_define(self.var_name, PralinePecanTerm(expr).evaluate(prog))
        result = self.body.evaluate(prog)
        prog.praline_local_cleanup([self.var_name])

        return result

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var_name == other.var_name and self.pecan_term == other.pecan_term and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.var_name, self.pecan_term, self.body))

class PralineLet(PralineTerm):
    def __init__(self, var_name : str, expr : PralineTerm, body : PralineTerm):
        super().__init__()
        self.var_name : str = var_name
        self.expr : PralineTerm = expr
        self.body : PralineTerm = body

    def transform(self, transformer : IRTransformer) -> PralineLet:
        return transformer.transform_PralineLet(self)

    def __str__(self) -> str:
        return '(let {} := {} in {})'.format(self.var_name, self.expr, self.body)

    def evaluate(self, prog : Program) -> PralineTerm:
        prog.praline_local_define(self.var_name, self.expr.evaluate(prog))
        result = self.body.evaluate(prog)
        prog.praline_local_cleanup([self.var_name])
        return result

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var_name == other.var_name and self.expr == other.expr and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.var_name, self.expr, self.body))

class Closure(PralineTerm):
    def __init__(self, env : dict[str, PralineTerm], args : list[PralineVar], body : PralineTerm):
        super().__init__()
        self.env : dict[str, PralineTerm] = env
        self.args : list[PralineVar] = args
        self.body : PralineTerm = body

    def evaluate(self, prog : Program) -> PralineTerm:
        if self.args: # If we still require more arguments
            return self
        else: # Evaluate as though we are in the environment specified
            prog.praline_local_define_all(self.env)
            result = self.body.evaluate(prog)
            prog.praline_local_cleanup(self.env.keys())
            return result

    def transform(self, transformer : IRTransformer) -> Closure:
        return transformer.transform_Closure(self)

    def __str__(self) -> str:
        return 'Closure({}, {}, {})'.format(self.env, self.args, self.body)

    def apply(self, prog : Program, arg : PralineTerm) -> PralineTerm:
        if not self.args:
            raise ValueError('Closure accepts no arguments!')

        new_env = dict(self.env)
        new_env[self.args[0].var_name] = arg

        if len(self.args) == 1:
            prog.enter_praline_env(new_env)
            result = self.body.evaluate(prog)
            prog.exit_praline_env()
            return result
        else:
            return Closure(new_env, self.args[1:], self.body)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.env == other.env and self.args == other.args and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.args, self.body))

class Builtin(PralineTerm):
    def __init__(self, name : PralineVar, args : list[PralineVar]):
        super().__init__()
        self.name : PralineVar = name
        self.args : list[PralineVar] = args

    def transform(self, transformer : IRTransformer) -> Builtin:
        return transformer.transform_Builtin(self)

    def __str__(self) -> str:
        return 'BUILTIN({})'.format(self.name)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.name == other.name and self.args == other.args

    def __hash__(self) -> int:
        return hash(self.name)

    def definition(self) -> PralineDef:
        return PralineDef(self.name, self.args, self)

class PralineDo(PralineTerm):
    def __init__(self, terms : list[PralineTerm]):
        super().__init__()
        self.terms : list[PralineTerm] = terms

    def transform(self, transformer : IRTransformer) -> PralineDo:
        return transformer.transform_PralineDo(self)

    def __str__(self) -> str:
        return 'do\n    {}'.format('\n    '.join(map(str, self.terms)))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.terms == other.terms

    def __hash__(self) -> int:
        return hash((self.terms))

    def evaluate(self, prog : Program) -> PralineTerm:
        result = PralineDummy()

        for term in self.terms:
            result = term.evaluate(prog)

        return result

class PralineAutomaton(PralineTerm):
    def __init__(self, input_names : list[str], input_bases : list[int], states : list[State], state_map : dict[str, int]):
        super().__init__()
        self.input_names : list[str] = input_names
        self.input_bases : list[int] = input_bases
        self.alphabet_line : str = ' '.join('{' + ', '.join(map(str, range(base))) + '}' for base in input_bases)

        self.states : list[State] = states
        self.state_map : dict[str, int] = state_map
        self.state_idx : int = len(self.states)

    def transform(self, transformer : IRTransformer) -> PralineAutomaton:
        return transformer.transform_PralineAutomaton(self)

    def __str__(self) -> str:
        return 'PralineAutomaton({}, {}, {}, {})'.format(self.input_names, self.input_bases, self.state_map, self.states)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.input_bases == other.input_bases and self.alphabet_line == other.alphabet_line and self.states == other.states and self.state_idx == other.state_idx and self.state_map == other.state_map and self.input_names == other.input_names

    def __hash__(self) -> int:
        return hash((self.alphabet_line, self.state_idx, len(self.states)))

    def evaluate(self, prog : Program) -> PralineAutomaton:
        return self

    def add_state(self, state_line : str) -> PralineAutomaton:
        new_state = State(self.state_idx, state_line)
        self.states.append(new_state)
        self.state_map[new_state.label] = self.state_idx

        self.state_idx += 1

        return self

    def add_transition(self, state_label : str, transition_line : str) -> PralineAutomaton:
        if state_label not in self.state_map:
            raise KeyError('No state "{}" in {}'.format(state_label, self))

        self.states[self.state_map[state_label]].add_transition(Transition(len(self.input_names), transition_line))

        return self

    def build(self) -> BuchiAutomaton:
        return build_aut(self.alphabet_line, self.states, self.state_map, self.input_names)
