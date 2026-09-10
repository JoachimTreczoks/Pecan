
from pecan.lang.ir.base import UnaryIRExpression, UnaryIRPredicate, BinaryIRExpression, BinaryIRPredicate, IRComparison
from pecan.lang.ir.praline.base import PralineIRNode, PralineTerm, PralineDummy
from pecan.lang.ir.praline.variables import PralineTuple, PralineList, PralinePecanLiteral

from pecan.exceptions import MatchingError

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.base import IRExpression, IRPredicate
    from pecan.lang.ir.prog import Program
    from pecan.lang.ir.praline.variables import PralineInt, PralineString, PralineVar
    from pecan.lang.ir.praline.functional import PralineApp, PralinePecanTerm


class PralineMatch(PralineTerm):
    def __init__(self, t : PralineTerm, arms : list[PralineMatchArm]):
        super().__init__()
        self.t : PralineTerm = t
        self.arms : list[PralineMatchArm] = arms

    def transform(self, transformer : IRTransformer) -> PralineMatch:
        return transformer.transform_PralineMatch(self)

    def __str__(self) -> str:
        return 'match {} with\n{}\nend'.format(self.t, '\n'.join(map(str, self.arms)))

    def evaluate(self, prog : Program) -> PralineTerm:
        eval_t = self.t.evaluate(prog)

        for arm in self.arms:
            match_env = arm.match(eval_t, prog)

            if match_env is not None:
                prog.praline_local_define_all(match_env)
                result = arm.expr.evaluate(prog)
                prog.praline_local_cleanup(match_env.keys())
                return result

        raise MatchingError('Inexhaustive match arms in "{}" (got "{}")'.format(self, eval_t))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.t == other.t and self.arms == other.arms

    def __hash__(self) -> int:
        return hash((self.t, self.arms))

class PralineMatchArm(PralineIRNode):
    def __init__(self, pat : PralineMatchPat, expr : PralineTerm):
        super().__init__()
        self.pat : PralineMatchPat = pat
        self.expr : PralineTerm = expr

    def match(self, term : PralineTerm, prog : Program) -> dict | None:
        return self.pat.match(term, prog)

    def transform(self, transformer : IRTransformer) -> PralineMatchArm:
        return transformer.transform_PralineMatchArm(self)

    def __str__(self) -> str:
        return 'case {} => {}'.format(self.pat, self.expr)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.pat == other.pat and self.expr == other.expr

    def __hash__(self) -> int:
        return hash((self.pat, self.expr))

class PralineMatchPat(PralineIRNode):
    def __init__(self):
        super().__init__()

    def match(self, term : PralineTerm, prog : Program) -> dict | None:
        raise NotImplementedError()

class PralineMatchInt(PralineMatchPat):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val

    def match(self, term : PralineInt, prog : Program) -> dict | None:
        if term.is_int() and term.get_int() == self.val:
            return {}
        else:
            return None

    def transform(self, transformer : IRTransformer) -> PralineMatchInt:
        return transformer.transform_PralineMatchInt(self)

    def __str__(self) -> str:
        return 'PralineMatchInt({})'.format(self.val)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.val == other.val

    def __hash__(self) -> int:
        return hash((self.val))

class PralineMatchPecan(PralineMatchPat):
    def __init__(self, pecan_term : PralinePecanTerm):
        super().__init__()
        self.pecan_term : PralinePecanTerm = pecan_term

    def match(self, term : PralinePecanTerm, prog : Program) -> dict | None:
        evaluated_term = self.pecan_term.evaluate(prog)
        if not isinstance(term, PralinePecanLiteral):
            return None

        return self.unify_terms(evaluated_term.pecan_term, term.pecan_term)

    def unify_terms[T : IRExpression | IRPredicate | None](self, term_a : T, term_b : T) -> dict | None:
        if term_a == None and term_b == None:
            return {}

        from pecan.lang.ir.prog import VarRef
        if isinstance(term_a, VarRef):
            return {term_a.var_name: term_b}

        if type(term_a) is not type(term_b):
            return None

        if isinstance(term_a, UnaryIRExpression):
            return self.unify_terms(term_a.a, term_b.a)
        if isinstance(term_a, BinaryIRExpression):
            return self.combine_unification(self.unify_terms(term_a.a, term_b.a), self.unify_terms(term_a.b, term_b.b))
        if isinstance(term_a, UnaryIRPredicate):
            return self.unify_terms(term_a.a, term_b.a)
        if isinstance(term_a, BinaryIRPredicate):
            return self.combine_unification(self.unify_terms(term_a.a, term_b.a), self.unify_terms(term_a.b, term_b.b))
        if isinstance(term_a, IRComparison):
            return self.combine_unification(self.unify_terms(term_a.a, term_b.a), self.unify_terms(term_a.b, term_b.b))

        from pecan.lang.ir.bool import BoolConst
        if isinstance(term_a, BoolConst):
            if term_a.bool_val == term_b.bool_val:
                return {}
            else:
                return None

        from pecan.lang.ir.quant import Exists
        if isinstance(term_a, Exists):
            unif = {}
            for var_a, var_b in zip(term_a.var_refs, term_b.var_refs):
                unif = self.combine_unification(unif, self.unify_terms(var_a, var_b))
            for cond_a, cond_b in zip(term_a.conds, term_b.conds):
                unif = self.combine_unification(unif, self.unify_terms(cond_a, cond_b))
            return self.combine_unification(unif, self.unify_terms(term_a.pred, term_b.pred))

        from pecan.lang.ir.prog import Call
        if isinstance(term_a, Call):
            unif = {}
            # if term_a.name.startswith('$'):
            #     unif[term_a.name] = PralineString(term_b.name)
            if term_a.name != term_b.name:
                return None

            for arg_a, arg_b in zip(term_a.args, term_b.args):
                unif = self.combine_unification(unif, self.unify_terms(arg_a, arg_b))
            return unif

        raise MatchingError('Unsupported Pecan term on LHS of a match arm: {}'.format(term_a))

    def combine_unification(self, unif_a : dict, unif_b : dict) -> dict | None:
        unif = {}

        for k, v in unif_a.items():
            if k not in unif_b or unif_b[k] == v:
                unif[k] = v
            else:
                return None

        for k, v in unif_b.items():
            if k not in unif_a or unif_a[k] == v:
                unif[k] = v
            else:
                return None

        return unif

    def transform(self, transformer : IRTransformer) -> PralineMatchPecan:
        return transformer.transform_PralineMatchPecan(self)

    def __str__(self) -> str:
        return 'PralineMatchPecan({})'.format(self.pecan_term)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.pecan_term == other.pecan_term

    def __hash__(self) -> int:
        return hash(self.pecan_term)

class PralineMatchString(PralineMatchPat):
    def __init__(self, val : str):
        super().__init__()
        self.val : str = val

    def match(self, term : PralineString, prog : Program) -> dict | None:
        if term.is_string() and term.get_string() == self.val:
            return {}
        else:
            return None

    def transform(self, transformer : IRTransformer) -> PralineMatchString:
        return transformer.transform_PralineMatchString(self)

    def __str__(self) -> str:
        return 'PralineMatchString({})'.format(self.val)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.val == other.val

    def __hash__(self) -> int:
        return hash((self.val))

class PralineMatchList(PralineMatchPat):
    def __init__(self, head : PralineMatchPat, tail : PralineMatchPat):
        super().__init__()
        self.head : PralineMatchPat | PralineDummy = head or PralineDummy()
        self.tail : PralineMatchPat | PralineDummy = tail or PralineDummy()

    def match(self, term : PralineList, prog : Program) -> dict | None:

        if not isinstance(term, PralineList):
            return None

        if isinstance(self.head, PralineDummy) or isinstance(term.head, PralineDummy):
            if isinstance(self.head, PralineDummy) and isinstance(term.head, PralineDummy):
                return {}
            else:
                return None

        head_match_env = self.head.match(term.head, prog)

        if head_match_env is None:
            return None

        tail_match_env = self.tail.match(term.tail, prog)

        if tail_match_env is None:
            return None

        head_match_env.update(tail_match_env)

        return head_match_env

    def transform(self, transformer : IRTransformer) -> PralineMatchList:
        return transformer.transform_PralineMatchList(self)

    def __str__(self) -> str:
        return 'PralineMatchList({}, {})'.format(self.head, self.tail)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.head == other.head and self.tail == other.tail

    def __hash__(self) -> int:
        return hash((self.head, self.tail))

class PralineMatchTuple(PralineMatchPat):
    def __init__(self, vals : list[PralineMatchPat]):
        super().__init__()
        self.vals : list[PralineMatchPat] = vals

    def transform(self, transformer : IRTransformer) -> PralineMatchTuple:
        return transformer.transform_PralineMatchTuple(self)

    def __str__(self) -> str:
        return 'PralineMatchTuple({})'.format(', '.join(map(str, self.vals)))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.vals == other.vals

    def __hash__(self) -> int:
        return hash(self.vals)

    def match(self, term : PralineTuple, prog : Program) -> dict | None:

        if not isinstance(term, PralineTuple):
            return None

        if len(self.vals) != len(term.vals):
            return None

        match_env = {}

        for pat, t in zip(self.vals, term.vals):
            m = pat.match(t, prog)
            if m is None:
                return None
            match_env.update(m)

        return match_env

class PralineMatchVar(PralineMatchPat):
    def __init__(self, var : str):
        super().__init__()
        self.var : str = var

    def match(self, term : PralineTerm, prog : Program) -> dict:
        return {self.var: term}

    def transform(self, transformer : IRTransformer) -> PralineMatchVar:
        return transformer.transform_PralineMatchVar(self)

    def __str__(self) -> str:
        return '{}'.format(self.var)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var == other.var

    def __hash__(self) -> int:
        return hash((self.var))

class PralineIf(PralineTerm):
    def __init__(self, cond : PralineApp | PralineVar, e1 : PralineTerm, e2 : PralineTerm):
        super().__init__()
        self.cond : PralineApp | PralineVar = cond
        self.e1 : PralineTerm = e1
        self.e2 : PralineTerm = e2

    def transform(self, transformer : IRTransformer) -> PralineIf:
        return transformer.transform_PralineIf(self)

    def __str__(self) -> str:
        return '(if {} then {} else {})'.format(self.cond, self.e1, self.e2)

    def evaluate(self, prog : Program) -> PralineTerm:
        cond_eval = self.cond.evaluate(prog)
        if cond_eval.is_bool():
            if cond_eval.get_bool():
                return self.e1.evaluate(prog)
            else:
                return self.e2.evaluate(prog)
        else:
            raise TypeError('cond should evaluate to a bool in "{}", got "{}"'.format(self, cond_eval))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.cond == other.cond and self.e1 == other.e1 and self.e2 == other.e2

    def __hash__(self) -> int:
        return hash((self.cond, self.e1, self.e2))