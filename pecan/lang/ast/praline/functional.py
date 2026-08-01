
from pecan.lang.ast.praline.base import PralineTerm, PralineASTNode
from pecan.lang.ast.praline.match import PralineMatch, PralineMatchArm
from pecan.lang.ast.praline.variables import PralineVar, PralineTuple

from pecan.exceptions import PralineLogicError

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer
    from pecan.lang.ast.base import ASTNode
    from pecan.lang.ast.praline.match import PralineMatchPecan

def process_args(app : PralineApp | PralineVar, body : PralineTerm) -> tuple[list[PralineVar], PralineTerm]:
    if isinstance(app, PralineApp):
        rest_args, new_body = process_args(app.receiver, body)
        new_arg, final_body = split_arg(app.arg, new_body)
        return rest_args + [new_arg], final_body
    else:
        return [app], body

def split_arg(arg : PralineTerm, body : PralineTerm) -> tuple[PralineVar, PralineTerm]:
    if isinstance(arg, PralineVar):
        return arg, body
    elif isinstance(arg, PralineTuple):
        placeholder_arg = PralineVar(PralineTerm.fresh_name())
        return placeholder_arg, PralineMatch(placeholder_arg, [PralineMatchArm(arg.build_match(), body)])
    else:
        raise PralineLogicError('Unexpected term in argument position: {}'.format(arg))

class PralineAlias(PralineASTNode):
    def __init__(self, name : str, directive_name : str, term : PralineTerm):
        super().__init__()
        self.name : str = name
        self.directive_name : str = directive_name
        self.term : PralineTerm = term

    def transform(self, transformer : AstTransformer) -> PralineAlias:
        return transformer.transform_PralineAlias(self)

    def __str__(self) -> str:
        return 'Alias "{}" ==> {} {} .'.format(self.name, self.directive_name, self.term)

class PralineDirective(PralineASTNode):
    def __init__(self, name : str, term : PralineTerm):
        super().__init__()
        self.name : str = name
        self.term : PralineTerm = term

    def transform(self, transformer : AstTransformer) -> PralineDirective:
        return transformer.transform_PralineDirective(self)

    def __str__(self) -> str:
        return '{} {} .'.format(self.name, self.term)

class PralineDef(PralineASTNode):
    def __init__(self, def_id : PralineApp | PralineVar, body : PralineTerm):
        def_params, new_body = process_args(def_id, body)

        self.name : PralineVar = def_params[0]
        self.args : list[PralineVar] = def_params[1:]
        self.body : PralineTerm = new_body

    def transform(self, transformer : AstTransformer) -> PralineDef:
        return transformer.transform_PralineDef(self)

    def __str__(self) -> str:
        return 'Define {} {} := {} .'.format(self.name, self.args, self.body)

class PralineApp(PralineTerm):
    def __init__(self, receiver : PralineApp | PralineVar, arg : PralineTerm):
        super().__init__()
        self.receiver : PralineApp | PralineVar = receiver
        self.arg : PralineTerm = arg

    def transform(self, transformer : AstTransformer) -> PralineApp:
        return transformer.transform_PralineApp(self)

    def __str__(self) -> str:
        return '({} {})'.format(self.receiver, self.arg)

class PralineIf(PralineTerm):
    def __init__(self, cond : PralineApp, e1 : PralineTerm, e2 : PralineTerm):
        super().__init__()
        self.cond : PralineApp = cond
        self.e1 : PralineTerm = e1
        self.e2 : PralineTerm = e2

    def transform(self, transformer : AstTransformer) -> PralineIf:
        return transformer.transform_PralineIf(self)

    def __str__(self) -> str:
        return '(if {} then {} else {})'.format(self.cond, self.e1, self.e2)

class PralinePecanTerm(PralineTerm):
    def __init__(self, pecan_term : ASTNode):
        super().__init__()
        self.pecan_term : ASTNode = pecan_term

    def transform(self, transformer : AstTransformer) -> PralinePecanTerm:
        return transformer.transform_PralinePecanTerm(self)

    def build_match(self) -> PralineMatchPecan:
        return PralineMatchPecan(self)

    def __str__(self) -> str:
        return '{{ {} }}'.format(self.pecan_term)

class PralineLambda(PralineTerm):
    def __init__(self, params : PralineVar, body : PralineTerm):
        super().__init__()
        self.params, self.body = process_args(params, body)

    def transform(self, transformer : AstTransformer) -> PralineLambda:
        return transformer.transform_PralineLambda(self)

    def __str__(self) -> str:
        return '(\\ {} -> {})'.format(self.params, self.body)

class PralineLetPecan(PralineTerm):
    def __init__(self, var_name : str, pecan_term : PralinePecanTerm, body : PralineTerm):
        super().__init__()
        self.var_name : str = var_name
        self.pecan_term : PralinePecanTerm = pecan_term
        self.body : PralineTerm = body

    def transform(self, transformer : AstTransformer) -> PralineLetPecan:
        return transformer.transform_PralineLetPecan(self)

    def __str__(self) -> str:
        return '(let {} be {} in {})'.format(self.var_name, self.pecan_term, self.body)

class PralineLet(PralineTerm):
    def __init__(self, var_name : str, expr : PralineTerm, body : PralineTerm):
        super().__init__()
        self.var_name : str = var_name
        self.expr : PralineTerm = expr
        self.body : PralineTerm = body

    def transform(self, transformer : AstTransformer) -> PralineLet:
        return transformer.transform_PralineLet(self)

    def __str__(self) -> str:
        return '(let {} := {} in {})'.format(self.var_name, self.expr, self.body)

class PralineDo(PralineTerm):
    def __init__(self, terms : list[PralineApp | PralineVar]):
        super().__init__()
        self.terms : list[PralineApp | PralineVar] = terms

    def transform(self, transformer : AstTransformer) -> PralineDo:
        return transformer.transform_PralineDo(self)

    def __str__(self) -> str:
        return 'do\n    {}'.format('\n    '.join(map(str, self.terms)))

