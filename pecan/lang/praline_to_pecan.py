#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ir_transformer import IRTransformer
from pecan.lang.ast_to_ir import ASTToIR

from pecan.lang.ast import *

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Never
    from pecan.lang.ast.base import ASTNode
    from pecan.lang.ir.base import IRNode
    import pecan.lang.ir as ir

class PralineToPecan(IRTransformer):
    def __init__(self):
        super().__init__()
        self.ast_to_ir : ASTToIR = ASTToIR()

    def to_ir(self, node : ASTNode) -> IRNode:
        return self.ast_to_ir.transform(node)

    def transform_PralineDef(self, node : PralineDef) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineApp(self, node : PralineApp) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineAdd(self, node : PralineAdd) -> PralineAdd:
        return self.to_ir(Add(self.transform(node.a), self.transform(node.b)))

    def transform_PralineSub(self, node : PralineSub) -> PralineSub:
        return self.to_ir(Sub(self.transform(node.a), self.transform(node.b)))

    def transform_PralineMul(self, node : PralineMul) -> PralineMul:
        return self.to_ir(Mul(self.transform(node.a), self.transform(node.b)))

    def transform_PralineDiv(self, node : PralineDiv) -> PralineDiv:
        return self.to_ir(Div(self.transform(node.a), self.transform(node.b)))

    def transform_PralineExponent(self, node : PralineExponent) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineNeg(self, node : PralineNeg) -> ir.Sub:
        return self.to_ir(Neg(self.transform(node.a), self.transform(node.b)))

    def transform_PralineList(self, node : PralineList) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatch(self, node : PralineMatch) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatchArm(self, node : PralineMatchArm) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatchInt(self, node : PralineMatchInt) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatchString(self, node : PralineMatchString) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatchList(self, node : PralineMatchString) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatchVar(self, node : PralineMatchVar) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineMatchPecan(self, node : PralineMatchPecan) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineIf(self, node : PralineIf) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralinePecanTerm(self, node : PralinePecanTerm) -> Never:
        # Note: We can't do this because we need to know the environment to evaluate in.
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralinePecanLiteral(self, node):
        return node.get_term()

    def transform_PralineLambda(self, node : PralineLambda) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineLetPecan(self, node : PralineLetPecan) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineLet(self, node : PralineLet) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineTuple(self, node : PralineTuple) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineVar(self, node : PralineVar) -> ir.VarRef:
        return self.to_ir(VarRef(node.var_name))

    def transform_PralineInt(self, node : PralineInt) -> ir.IntConst:
        return self.to_ir(IntConst(node.val))

    def transform_PralineString(self, node : PralineString) -> ir.VarRef:
        return self.to_ir(VarRef(node.val))

    def transform_PralineBool(self, node : PralineBool) -> ir.BoolConst:
        return self.to_ir(BoolConst(node.val))

    def transform_PralineDo(self, node : PralineDo) -> Never:
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

    def transform_PralineAutomaton(self, node):
        raise Exception('"{}" cannot be translated into to Pecan'.format(node))

