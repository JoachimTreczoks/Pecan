
from pecan.lang.ast.praline.base import PralineBinaryOp, PralineUnaryOp

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer
    from pecan.lang.ast.praline.base import PralineTerm

class PralineAdd(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineAdd:
        return transformer.transform_PralineAdd(self)

    def __str__(self) -> str:
        return '({} + {})'.format(self.a, self.b)

class PralineDiv(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineDiv:
        return transformer.transform_PralineDiv(self)

    def __str__(self) -> str:
        return '({} / {})'.format(self.a, self.b)

class PralineSub(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineSub:
        return transformer.transform_PralineSub(self)

    def __str__(self) -> str:
        return '({} - {})'.format(self.a, self.b)

class PralineMul(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineMul:
        return transformer.transform_PralineMul(self)

    def __str__(self) -> str:
        return '({} * {})'.format(self.a, self.b)

class PralineExponent(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : AstTransformer) -> PralineExponent:
        return transformer.transform_PralineExponent(self)

    def __str__(self) -> str:
        return '({} ^ {})'.format(self.a, self.b)

class PralineNeg(PralineUnaryOp):
    def __init__(self, a : PralineTerm):
        super().__init__(a)

    def transform(self, transformer : AstTransformer) -> PralineNeg:
        return transformer.transform_PralineNeg(self)

    def __str__(self) -> str:
        return '(-{})'.format(self.a)
