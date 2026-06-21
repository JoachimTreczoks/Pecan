#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast.base import ASTNode

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer
    from pecan.lang.ast.prog import Predicate

def process_args(app : PralineTerm, body : PralineTerm) -> tuple[list[PralineTerm], PralineTerm]:
    if isinstance(app, PralineApp):
        rest_args, new_body = process_args(app.receiver, body)
        new_arg, final_body = split_arg(app.arg, new_body)
        return rest_args + [new_arg], final_body
    else:
        return [app], body

def split_arg(arg : PralineTuple | PralineVar, body : PralineTerm) -> tuple[PralineVar, PralineTerm]:
    if isinstance(arg, PralineVar):
        return arg, body
    elif isinstance(arg, PralineTuple):
        placeholder_arg = PralineVar(PralineTerm.fresh_name())
        return placeholder_arg, PralineMatch(placeholder_arg, [PralineMatchArm(arg.build_match(), body)])
    else:
        raise Exception('Unexpected term in argument position: {}'.format(arg))

class PralineTerm(ASTNode):
    var_counter = 0
    @staticmethod
    def fresh_name() -> str:
        label = "__arg{}".format(PralineTerm.var_counter)
        PralineTerm.var_counter += 1
        return label

    def __init__(self):
        super().__init__()

    def build_match(self) -> PralineMatchPat:
        raise NotImplementedError

class PralineAlias(ASTNode):
    def __init__(self, name : str, directive_name : str, term : PralineTerm):
        super().__init__()
        self.name : str = name
        self.directive_name : str = directive_name
        self.term : PralineTerm = term

    def transform(self, transformer : AstTransformer) -> PralineAlias:
        return transformer.transform_PralineAlias(self)

    def show(self) -> str:
        return 'Alias "{}" ==> {} {} .'.format(self.name, self.directive_name, self.term)

class PralineDirective(ASTNode):
    def __init__(self, name : str, term : PralineTerm):
        super().__init__()
        self.name : str = name
        self.term : PralineTerm = term

    def transform(self, transformer : AstTransformer) -> PralineDirective:
        return transformer.transform_PralineDirective(self)

    def show(self) -> str:
        return '{} {} .'.format(self.name, self.term)

class PralineDef(ASTNode): # TODO: Type hinting
    def __init__(self, def_id : PralineTerm, body : PralineTerm):
        def_params, new_body = process_args(def_id, body)

        self.name : str = def_params[0]
        self.args : list[PralineVar] = def_params[1:]
        self.body : PralineApp = new_body

    def transform(self, transformer : AstTransformer) -> PralineDef:
        return transformer.transform_PralineDef(self)

    def show(self) -> str:
        return 'Define {} {} := {} .'.format(self.name, self.args, self.body)

class PralineApp(PralineTerm):
    def __init__(self, receiver : PralineTerm, arg : PralineTerm):
        super().__init__()
        self.receiver : PralineTerm = receiver
        self.arg : PralineTerm = arg

    def transform(self, transformer : AstTransformer) -> PralineApp:
        return transformer.transform_PralineApp(self)

    def show(self) -> str:
        return '({} {})'.format(self.receiver, self.arg)

class PralineVar(PralineTerm):
    def __init__(self, var_name : str):
        super().__init__()
        self.var_name : str = var_name

    def transform(self, transformer : AstTransformer) -> PralineVar:
        return transformer.transform_PralineVar(self)

    def build_match(self) -> PralineMatchVar:
        return PralineMatchVar(self.var_name)

    def show(self) -> str:
        return '{}'.format(self.var_name)

class PralineBinaryOp(PralineTerm):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__()
        self.a : PralineTerm = a
        self.b : PralineTerm = b

class PralineAdd(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineAdd:
        return transformer.transform_PralineAdd(self)

    def show(self) -> str:
        return '({} + {})'.format(self.a, self.b)

class PralineDiv(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineDiv:
        return transformer.transform_PralineDiv(self)

    def show(self) -> str:
        return '({} / {})'.format(self.a, self.b)

class PralineSub(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineSub:
        return transformer.transform_PralineSub(self)

    def show(self) -> str:
        return '({} - {})'.format(self.a, self.b)

class PralineMul(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineMul:
        return transformer.transform_PralineMul(self)

    def show(self) -> str:
        return '({} * {})'.format(self.a, self.b)

class PralineExponent(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineExponent:
        return transformer.transform_PralineExponent(self)

    def show(self) -> str:
        return '({} ^ {})'.format(self.a, self.b)

class PralineUnaryOp(PralineTerm):
    def __init__(self, a : PralineTerm):
        super().__init__()
        self.a : PralineTerm = a

class PralineNeg(PralineUnaryOp):
    def __init__(self, a : PralineTerm):
        super().__init__(a)

    def transform(self, transformer : AstTransformer) -> PralineNeg:
        return transformer.transform_PralineNeg(self)

    def show(self) -> str:
        return '(-{})'.format(self.a)

class PralineList(PralineTerm):
    def __init__(self, head : PralineTerm | None, tail : PralineTerm | None):
        super().__init__()
        self.head : PralineTerm | None = head
        self.tail : PralineTerm | None = tail

    def transform(self, transformer : AstTransformer) -> PralineList:
        return transformer.transform_PralineList(self)

    def build_match(self) -> PralineMatchList:
        return PralineMatchList(self.head.build_match(), self.tail.build_match())

    def show(self) -> str:
        if self.head is None:
            return '[]'
        else:
            return '({} :: {})'.format(self.head, self.tail)

class PralineMatch(PralineTerm):
    def __init__(self, t : PralineTerm, arms : list[PralineMatchArm]):
        super().__init__()
        self.t : PralineTerm = t
        self.arms : list[PralineMatchArm] = arms

    def transform(self, transformer : AstTransformer) -> PralineMatch:
        return transformer.transform_PralineMatch(self)

    def show(self) -> str:
        return 'match {} with\n{}\nend'.format(self.t, '\n'.join(map(repr, self.arms)))

class PralineMatchArm(ASTNode):
    def __init__(self, pat : PralineMatchPat, expr : PralineTerm):
        super().__init__()
        self.pat : PralineMatchPat = pat
        self.expr : PralineTerm = expr

    def transform(self, transformer : AstTransformer) -> PralineMatchArm:
        return transformer.transform_PralineMatchArm(self)

    def show(self) -> str:
        return 'case {} => {}'.format(self.pat, self.expr)

class PralineMatchPat(ASTNode):
    def __init__(self):
        super().__init__()

class PralineMatchInt(PralineMatchPat):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val

    def transform(self, transformer : AstTransformer) -> PralineMatchInt:
        return transformer.transform_PralineMatchInt(self)

    def show(self) -> str:
        return 'PralineMatchInt({})'.format(self.val)

class PralineMatchString(PralineMatchPat):
    def __init__(self, val : str):
        super().__init__()
        self.val : str = val

    def transform(self, transformer : AstTransformer) -> PralineMatchString:
        return transformer.transform_PralineMatchString(self)

    def show(self) -> str:
        return 'PralineMatchString({})'.format(self.val)

class PralineMatchList(PralineMatchPat):
    def __init__(self, head : PralineMatchPat | None, tail : PralineMatchPat | None):
        super().__init__()
        self.head : PralineMatchPat | None = head
        self.tail : PralineMatchPat | None = tail

    def transform(self, transformer : AstTransformer) -> PralineMatchList:
        return transformer.transform_PralineMatchList(self)

    def show(self) -> str:
        return 'PralineMatchList({}, {})'.format(self.head, self.tail)

class PralineMatchTuple(PralineMatchPat):
    def __init__(self, vals : list[PralineTerm]):
        super().__init__()
        self.vals : list[PralineTerm] = vals

    def transform(self, transformer : AstTransformer) -> PralineMatchTuple:
        return transformer.transform_PralineMatchTuple(self)

    def show(self) -> str:
        return 'PralineMatchTuple({})'.format(','.join(map(repr, self.vls)))

class PralineMatchVar(PralineMatchPat):
    def __init__(self, var : str):
        super().__init__()
        self.var : str = var

    def transform(self, transformer : AstTransformer) -> PralineMatchVar:
        return transformer.transform_PralineMatchVar(self)

    def show(self) -> str:
        return 'PralineMatchVar({})'.format(self.var)

class PralineMatchPecan(PralineMatchPat):
    def __init__(self, pecan_term : Predicate):
        super().__init__()
        self.pecan_term : Predicate = pecan_term

    def transform(self, transformer : AstTransformer) -> PralineMatchPecan:
        return transformer.transform_PralineMatchPecan(self)

    def show(self) -> str:
        return 'PralineMatchPecan({})'.format(self.pecan_term)

class PralineIf(PralineTerm):
    def __init__(self, cond : PralineApp, e1 : PralineTerm, e2 : PralineTerm):
        super().__init__()
        self.cond : PralineApp = cond
        self.e1 : PralineTerm = e1
        self.e2 : PralineTerm = e2

    def transform(self, transformer : AstTransformer) -> PralineIf:
        return transformer.transform_PralineIf(self)

    def show(self) -> str:
        return '(if {} then {} else {})'.format(self.cond, self.e1, self.e2)

class PralinePecanTerm(PralineTerm):
    def __init__(self, pecan_term : Predicate):
        super().__init__()
        self.pecan_term : Predicate = pecan_term

    def transform(self, transformer : AstTransformer) -> PralinePecanTerm:
        return transformer.transform_PralinePecanTerm(self)

    def build_match(self) -> PralineMatchPecan:
        return PralineMatchPecan(self)

    def show(self) -> str:
        return '{{ {} }}'.format(self.pecan_term)

class PralineLambda(PralineTerm):
    def __init__(self, params : PralineVar, body : PralineTerm):
        super().__init__()
        self.params, self.body = process_args(params, body)

    def transform(self, transformer : AstTransformer) -> PralineLambda:
        return transformer.transform_PralineLambda(self)

    def show(self) -> str:
        return '(\\ {} -> {})'.format(self.params, self.body)

class PralineLetPecan(PralineTerm):
    def __init__(self, var_name : str, pecan_term : Predicate, body : PralineTerm):
        super().__init__()
        self.var_name : str = var_name
        self.pecan_term : Predicate = pecan_term
        self.body : PralineTerm = body

    def transform(self, transformer : AstTransformer) -> PralineLetPecan:
        return transformer.transform_PralineLetPecan(self)

    def show(self) -> str:
        return '(let {} be {} in {})'.format(self.var_name, self.pecan_term, self.body)

class PralineLet(PralineTerm):
    def __init__(self, var_name : str, expr : PralineTerm, body : PralineTerm):
        super().__init__()
        self.var_name : str = var_name
        self.expr : PralineTerm = expr
        self.body : PralineTerm = body

    def transform(self, transformer : AstTransformer) -> PralineLet:
        return transformer.transform_PralineLet(self)

    def show(self) -> str:
        return '(let {} := {} in {})'.format(self.var_name, self.expr, self.body)

class PralineTuple(PralineTerm):
    def __init__(self, vals : list[PralineTerm]):
        super().__init__()
        self.vals : list[PralineTerm] = vals

    def build_match(self) -> PralineMatchTuple:
        return PralineMatchTuple([v.build_match() for v in self.vals])

    def transform(self, transformer : AstTransformer) -> PralineTuple:
        return transformer.transform_PralineTuple(self)

    def show(self) -> str:
        return '({})'.format(','.join(map(repr, self.vals)))

class PralineInt(PralineTerm):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val

    def transform(self, transformer : AstTransformer) -> PralineInt:
        return transformer.transform_PralineInt(self)

    def build_match(self) -> PralineMatchInt:
        return PralineMatchInt(self.val)

    def show(self) -> str:
        return 'PralineInt({})'.format(self.val)

class PralineString(PralineTerm):
    def __init__(self, val : str):
        super().__init__()
        self.val : str = val

    def transform(self, transformer : AstTransformer) -> PralineString:
        return transformer.transform_PralineString(self)

    def build_match(self) -> PralineMatchString:
        return PralineMatchString(self.val)

    def show(self):
        return 'PralineString({})'.format(self.val)

class PralineBool(PralineTerm):
    def __init__(self, val : bool):
        super().__init__()
        self.val : bool = val

    def transform(self, transformer : AstTransformer) -> PralineBool:
        return transformer.transform_PralineBool(self)

    def show(self) -> str:
        return 'PralineBool({})'.format(self.val)

class PralineDo(PralineTerm):
    def __init__(self, terms : list[PralineApp]):
        super().__init__()
        self.terms : list[PralineApp] = terms

    def transform(self, transformer : AstTransformer) -> PralineDo:
        return transformer.transform_PralineDo(self)

    def show(self) -> str:
        return 'do\n    {}'.format('\n    '.join(map(repr, self.terms)))

