
from pecan.lang.ast.praline.base import PralineTerm, PralineASTNode

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer
    from pecan.lang.ast.praline.functional import PralinePecanTerm

class PralineMatch(PralineTerm):
    def __init__(self, t : PralineTerm, arms : list[PralineMatchArm]):
        super().__init__()
        self.t : PralineTerm = t
        self.arms : list[PralineMatchArm] = arms

    def transform(self, transformer : AstTransformer) -> PralineMatch:
        return transformer.transform_PralineMatch(self)

    def __str__(self) -> str:
        return 'match {} with\n{}\nend'.format(self.t, '\n'.join(map(str, self.arms)))

class PralineMatchArm(PralineASTNode):
    def __init__(self, pat : PralineMatchPat, expr : PralineTerm):
        super().__init__()
        self.pat : PralineMatchPat = pat
        self.expr : PralineTerm = expr

    def transform(self, transformer : AstTransformer) -> PralineMatchArm:
        return transformer.transform_PralineMatchArm(self)

    def __str__(self) -> str:
        return 'case {} => {}'.format(self.pat, self.expr)

class PralineMatchPat(PralineASTNode):
    def __init__(self):
        super().__init__()

class PralineMatchInt(PralineMatchPat):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val

    def transform(self, transformer : AstTransformer) -> PralineMatchInt:
        return transformer.transform_PralineMatchInt(self)

    def __str__(self) -> str:
        return 'PralineMatchInt({})'.format(self.val)

class PralineMatchString(PralineMatchPat):
    def __init__(self, val : str):
        super().__init__()
        self.val : str = val

    def transform(self, transformer : AstTransformer) -> PralineMatchString:
        return transformer.transform_PralineMatchString(self)

    def __str__(self) -> str:
        return 'PralineMatchString({})'.format(self.val)

class PralineMatchList(PralineMatchPat):
    def __init__(self, head : PralineMatchPat | None, tail : PralineMatchPat | None):
        super().__init__()
        self.head : PralineMatchPat | None = head
        self.tail : PralineMatchPat | None = tail

    def transform(self, transformer : AstTransformer) -> PralineMatchList:
        return transformer.transform_PralineMatchList(self)

    def __str__(self) -> str:
        return 'PralineMatchList({}, {})'.format(self.head, self.tail)

class PralineMatchTuple(PralineMatchPat):
    def __init__(self, vals : list[PralineMatchPat]):
        super().__init__()
        self.vals : list[PralineMatchPat] = vals

    def transform(self, transformer : AstTransformer) -> PralineMatchTuple:
        return transformer.transform_PralineMatchTuple(self)

    def __str__(self) -> str:
        return 'PralineMatchTuple({})'.format(', '.join(map(str, self.vals)))

class PralineMatchVar(PralineMatchPat):
    def __init__(self, var : str):
        super().__init__()
        self.var : str = var

    def transform(self, transformer : AstTransformer) -> PralineMatchVar:
        return transformer.transform_PralineMatchVar(self)

    def __str__(self) -> str:
        return 'PralineMatchVar({})'.format(self.var)

class PralineMatchPecan(PralineMatchPat):
    def __init__(self, pecan_term : PralinePecanTerm):
        super().__init__()
        self.pecan_term : PralinePecanTerm = pecan_term

    def transform(self, transformer : AstTransformer) -> PralineMatchPecan:
        return transformer.transform_PralineMatchPecan(self)

    def __str__(self) -> str:
        return 'PralineMatchPecan({})'.format(self.pecan_term)
