
from pecan.lang.ir.praline.base import PralineBinaryOp, PralineUnaryOp, PralineDummy, PralineTerm
from pecan.lang.ir.praline.variables import PralineInt, PralineString

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.prog import Program


class PralineAdd(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : IRTransformer) -> PralineAdd:
        return transformer.transform_PralineAdd(self)

    def __str__(self) -> str:
        return '({} + {})'.format(self.a, self.b)

    def evaluate(self, prog : Program) -> PralineInt:
        eval_a = self.a.evaluate(prog)
        eval_b = self.b.evaluate(prog)

        if eval_a.is_int() and eval_b.is_int():
            return PralineInt(eval_a.get_int() + eval_b.get_int())
        else:
            raise TypeError('Both operands should be integers in "{}"'.format(self))

class PralineDiv(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : IRTransformer) -> PralineDiv:
        return transformer.transform_PralineDiv(self)

    def __str__(self) -> str:
        return '({} / {})'.format(self.a, self.b)

    def evaluate(self, prog : Program) -> PralineInt:
        eval_a = self.a.evaluate(prog)
        eval_b = self.b.evaluate(prog)

        if eval_a.is_int() and eval_b.is_int():
            return PralineInt(eval_a.get_int() // eval_b.get_int())
        else:
            raise TypeError('Both operands should be integers in "{}"'.format(self))

class PralineSub(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : IRTransformer) -> PralineSub:
        return transformer.transform_PralineSub(self)

    def __str__(self) -> str:
        return '({} - {})'.format(self.a, self.b)

    def evaluate(self, prog : Program) -> PralineInt:
        eval_a = self.a.evaluate(prog)
        eval_b = self.b.evaluate(prog)

        if eval_a.is_int() and eval_b.is_int():
            return PralineInt(eval_a.get_int() - eval_b.get_int())
        else:
            raise TypeError('Both operands should be integers in "{}"'.format(self))

class PralineMul(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : IRTransformer) -> PralineMul:
        return transformer.transform_PralineMul(self)

    def __str__(self) -> str:
        return '({} * {})'.format(self.a, self.b)

    def evaluate(self, prog : Program) -> PralineInt:
        eval_a = self.a.evaluate(prog)
        eval_b = self.b.evaluate(prog)

        if eval_a.is_int() and eval_b.is_int():
            return PralineInt(eval_a.get_int() * eval_b.get_int())
        else:
            raise TypeError('Both operands should be integers in "{}"'.format(self))

class PralineExponent(PralineBinaryOp):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__(a, b)

    def transform(self, transformer : IRTransformer) -> PralineExponent:
        return transformer.transform_PralineExponent(self)

    def __str__(self) -> str:
        return '({} ^ {})'.format(self.a, self.b)

    def evaluate(self, prog : Program) -> PralineInt | PralineString:
        eval_a = self.a.evaluate(prog)
        eval_b = self.b.evaluate(prog)

        if eval_a.is_int() and eval_b.is_int():
            return PralineInt(eval_a.get_int()**eval_b.get_int())
        elif eval_a.is_string() and eval_b.is_string():
            return PralineString(eval_a.get_string() + eval_b.get_string()) # + is for string concatenation
        else:
            raise TypeError('Both operands should be integers or strings in "{}", but they are ({} : {}) and ({} : {}), respectively.'.format(self, eval_a, eval_a.value_type, eval_b, eval_b.value_type))

class PralineNeg(PralineUnaryOp):
    def __init__(self, a : PralineTerm):
        super().__init__(a)

    def transform(self, transformer : IRTransformer) -> PralineNeg:
        return transformer.transform_PralineNeg(self)

    def __str__(self) -> str:
        return '(-{})'.format(self.a)

    def evaluate(self, prog : Program) -> PralineInt:
        temp = self.a.evaluate(prog)

        if not temp.is_int():
            raise TypeError('operand should evaluate to an integer in "{}"'.format(temp, self))

        return PralineInt(-temp.get_int())

