#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ir_transformer import IRTransformer
from pecan.lang.optimizer.basic_optimizer import BasicOptimizer

from pecan.lang.ir import *

class ArithmeticOptimizer(BasicOptimizer):
    def constant_eq(self, node : IRNode, val : int) -> bool:
        return isinstance(node, IntConst) and node.val == val

    def transform_Add(self, node : Add) -> IRExpression:
        if self.constant_eq(node.a, 0):
            self.changed = True
            return self.transform(node.b)
        elif self.constant_eq(node.b, 0):
            self.changed = True
            return self.transform(node.a)
        else:
            return Add(self.transform(node.a), self.transform(node.b)).with_type(node.get_type())

    def transform_Sub(self, node : Sub) -> IRExpression:
        if self.constant_eq(node.b, 0):
            self.changed = True
            return self.transform(node.a)
        else:
            return Sub(self.transform(node.a), self.transform(node.b)).with_type(node.get_type())

    def transform_Equals(self, node : Equals) -> IRPredicate:
        from pecan.lang.type_inference import UndefinedType
        # we can only do the following transformation once we know types, otherwise we will be unable to resolve the dynamic call to 'adder'
        if node.a.get_type() != UndefinedType() and node.b.get_type() != UndefinedType():
            if isinstance(node.a, VarRef) and isinstance(node.b, Add):
                self.changed = True
                return self.transform(Call('adder', [node.b.a, node.b.b, node.a]))
            elif isinstance(node.b, VarRef) and isinstance(node.a, Add):
                self.changed = True
                return self.transform(Call('adder', [node.a.a, node.a.b, node.b]))
            # elif isinstance(node.a, VarRef) and isinstance(node.b, Add):
            #     self.changed = True
            #     return self.transform(Call('adder', [node.a, node.b.b, node.b.a]))
            # isinstance(node.b, VarRef) and isinstance(node.a, Sub):
            #     self.changed = True
            #     return self.transform(Call('adder', [node.b, node.a.b, node.a.a]))

        return super().transform_Equals(node)

    def __str__(self) -> str:
        return 'ArithmeticOptimizer'
