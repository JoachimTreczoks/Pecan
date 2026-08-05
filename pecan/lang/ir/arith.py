#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

#from pecan.lang.ir import *

from pecan.lang.ir.base import BinaryIRExpression, IREvaluation, IRExpression, IRComparison
from pecan.lang.ir.bool import BoolConst, Complement, Conjunction, Disjunction
from pecan.lang.ir.prog import Call, VarRef
from pecan.lang.ir.quant import Exists

from pecan.exceptions import AutomatonArithmeticError

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.prog import Program

# From: https://stackoverflow.com/a/57027610/1498618
def is_power_of_two(n : int) -> bool:
    return (n != 0) and (n & (n-1) == 0)

# TODO: memoize same expressions
class Add(BinaryIRExpression):
    def __init__(self, a, b):
        super().__init__(a, b)

    def change_label(self, label : str) -> Add: # for changing label to __constant#
        self.label = label
        return self

    def __str__(self) -> str:
        return self.format_type('({} + {})'.format(self.a, self.b))

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.is_int and self.evaluate_int(prog) >= 0:
            return IntConst(self.evaluate_int(prog)).with_type(self.get_type()).evaluate(prog)

        res_a = self.a.evaluate(prog)
        res_b = self.b.evaluate(prog)

        aut_add = prog.call('adder', [res_a.ref, res_b.ref, self.label_var()])

        return IREvaluation(self.project_intermediates(prog, res_a.ref, res_b.ref, res_a.aut & res_b.aut & aut_add.aut), self.label_var())

    def transform(self, transformer : IRTransformer) -> Add:
        return transformer.transform_Add(self)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) + self.b.evaluate_int(prog)

class Sub(BinaryIRExpression):
    def __init__(self, a, b):
        super().__init__(a, b)

    def __str__(self) -> str:
        return self.format_type('({} - {})'.format(self.a, self.b))

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.is_int and self.evaluate_int(prog) >= 0:
            return IntConst(self.evaluate_int(prog)).with_type(self.get_type()).evaluate(prog)

        res_a = self.a.evaluate(prog)
        res_b = self.b.evaluate(prog)

        aut_sub = prog.call('adder', [self.label_var(), res_b.ref, res_a.ref])

        return IREvaluation(self.project_intermediates(prog, res_a.ref, res_b.ref, res_a.aut & res_b.aut & aut_sub.aut), self.label_var())

    def transform(self, transformer : IRTransformer) -> Sub:
        return transformer.transform_Sub(self)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) - self.b.evaluate_int(prog)

class Mul(BinaryIRExpression):
    def __init__(self, a, b):
        super().__init__(a, b)

    def change_label(self, label : str): # for changing label to __constant#
        self.label = label
        return self

    def __str__(self) -> str:
        return self.format_type('({} * {})'.format(self.a, self.b))

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.is_int:
            n = self.evaluate_int(prog)
            if n >= 0:
                return IntConst(n).with_type(self.get_type()).evaluate(prog)
            else:
                return Sub(IntConst(0), IntConst(n)).with_type(self.get_type()).evaluate(prog)

        if not self.a.is_int and not self.b.is_int:
            raise AutomatonArithmeticError("At least one argument of multiplication must be an constant integer in {}".format(self))

        # We assumed above that a was the int, but it might not be; if it wasn't, just swap the two
        if not self.a.is_int:
            self.a, self.b = self.b, self.a

        # We are guaranteed that self.a will be an integer, so we don't need to worry about transforming it
        c = self.a.evaluate_int(prog)  # copy of a

        negative = False

        if c == 0:
            return IntConst(0).with_type(self.get_type()).evaluate(prog)

        if c < 0:
            negative = True
            c = -c

        power = self.b

        s = IntConst(0).with_type(self.get_type())
        while True:
            if c & 1 == 1:
                s = Add(power, s).with_type(self.get_type())
            c = c // 2
            if c <= 0:
                break
            power = Add(power, power).with_type(self.get_type())

        if negative:
            return Sub(IntConst(0), s).with_type(self.get_type()).evaluate(prog)
        else:
            return s.evaluate(prog)

    def transform(self, transformer : IRTransformer) -> Mul:
        return transformer.transform_Mul(self)

    def evaluate_int(self, prog : Program) -> int:
        assert self.is_int
        return self.a.evaluate_int(prog) * self.b.evaluate_int(prog)

constants_map = {}
class IntConst(IRExpression):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val
        self.label : str = "__constant{}".format(self.val)

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.val < 0:
            return Sub(IntConst(0), IntConst(-self.val)).with_type(self.get_type()).evaluate(prog)

        if (self.val, self.get_type()) in constants_map:
            aut, ref = constants_map[(self.val, self.get_type())]
            return IREvaluation(aut, ref)

        if self.val == 0:
            res = prog.call('zero', [self.label_var()])
            constants_map[(self.val, self.get_type())] = (res.aut, self.label_var())
        elif self.val == 1:
            res = prog.lookup_dynamic_call('one', [self.label_var()])

            # This means we didn't find a user-defined "one", so just use the default expression
            if res.name == 'one':
                b_const = VarRef(prog.fresh_name()).with_type(self.get_type())
                zero_const = IntConst(0).with_type(self.get_type())

                leq = Disjunction(Less(self.label_var(), b_const), Equals(self.label_var(), b_const))
                b_in_0_1 = Conjunction(Less(zero_const, b_const), Less(b_const, self.label_var()))
                formula_1 = Conjunction(self.get_type().restrict(self.label_var()),
                                        Conjunction(Less(zero_const, self.label_var()),
                                            Complement(Exists([b_const], [self.get_type().restrict(b_const)], b_in_0_1))))
                constants_map[(self.val, self.get_type())] = (formula_1.evaluate(prog).aut, self.label_var())
            else:
                res = prog.call('one', [self.label_var()])
                constants_map[(self.val, self.get_type())] = (res.aut, self.label_var())
        else:
            assert self.val >= 2, "constant here should be greater than or equal to 2, while it is {}".format(self.val)

            if self.val & (self.val - 1) == 0:
                half = IntConst(self.val // 2)
                result = Add(half, half).with_type(self.get_type())
            else:
                c = self.val
                power = 1
                while c != 1:
                    power  = power << 1
                    c = c >> 1
                result = Add(IntConst(power), IntConst(self.val - power)).with_type(self.get_type())

            result.change_label(self.label)
            result.is_int = False
            evaluation = result.evaluate(prog)

            # because the powers of two get used so much, it is advantageous to make sure they are as small
            # as possible by postprocessing them
            if is_power_of_two(self.val):
                evaluation.postprocess()

            constants_map[(self.val, self.get_type())] = (evaluation.aut, evaluation.ref)

        aut, ref = constants_map[(self.val, self.get_type())]
        return IREvaluation(aut, ref)

    def evaluate_int(self, prog : Program) -> int:
        return self.val

    def transform(self, transformer : IRTransformer) -> IntConst:
        return transformer.transform_IntConst(self)

    def __str__(self) -> str:
        return self.format_type(str(self.val))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.val == other.val and self.get_type() == other.get_type()

    def __hash__(self) -> int:
        return hash(self.val)

class Equals(IRComparison):
    def __init__(self, a : IRExpression, b : IRExpression):
        super().__init__(a, b)

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.a.is_int and self.b.is_int:
            return BoolConst(self.a.evaluate_int(prog) == self.b.evaluate_int(prog)).evaluate(prog)

        res_a = self.a.evaluate(prog)
        res_b = self.b.evaluate(prog)

        eq_aut = prog.call('equal', [res_a.ref, res_b.ref])

        return IREvaluation(self.project_intermediates(prog, res_a.ref, res_b.ref, eq_aut.aut & res_a.aut & res_b.aut))

    def transform(self, transformer : IRTransformer) -> Equals:
        return transformer.transform_Equals(self)

    def __str__(self) -> str:
        return '({} = {})'.format(self.a, self.b)

class Less(IRComparison):
    def __init__(self, a : IRExpression, b : IRExpression):
        super().__init__(a, b)

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.a.is_int and self.b.is_int:
            return BoolConst(self.a.evaluate_int(prog) < self.b.evaluate_int(prog)).evaluate(prog)

        res_a = self.a.evaluate(prog)
        res_b = self.b.evaluate(prog)

        aut_less = prog.call('less', [res_a.ref, res_b.ref])

        return IREvaluation(self.project_intermediates(prog, res_a.ref, res_b.ref, res_a.aut & res_b.aut & aut_less.aut))

    def transform(self, transformer : IRTransformer) -> Less:
        return transformer.transform_Less(self)

    def __str__(self) -> str:
        return '({} < {})'.format(self.a, self.b)

class FunctionExpression(IRExpression):
    def __init__(self, pred_name, args, val_idx):
        super().__init__()
        self.is_int = False
        self.pred_name = pred_name
        self.args = args
        self.val_idx = val_idx # the index of the "return value" of the function
        # TODO: Warn users if the function is not a "true" function

    def evaluate_node(self, prog : Program) -> IREvaluation:
        return_val = VarRef(prog.fresh_name()).with_type(self.args[self.val_idx].get_type())
        self.args[self.val_idx] = return_val
        from pecan.lang.typed_ir_lowering import TypedIRLowering
        return TypedIRLowering(prog).transform(Call(self.pred_name, self.args)).evaluate(prog).with_ref(return_val)

    # Transforms the function expression into a regular call, with the result going into the variable provided.
    # For example: if we have something like P() = x, we probably want to transform this into just P(x)
    def to_call(self, result_var) -> Call:
        self.args[self.val_idx] = result_var
        return Call(self.pred_name, self.args)

    def transform(self, transformer : IRTransformer) -> FunctionExpression:
        return transformer.transform_FunctionExpression(self)

    def __str__(self) -> str:
        temp_args = list(map(str, self.args))
        temp_args[self.val_idx] = 'out({})'.format(self.args[self.val_idx])
        return self.format_type('{}({})'.format(self.pred_name, ', '.join(temp_args)))

class PredicateExpr(IRExpression):
    def __init__(self, var : VarRef, pred):
        super().__init__()
        from pecan.lang.ir_substitution import IRSubstitution # TODO: Check what is up with this import
        self.var : VarRef = var
        self.pred = pred
        self.is_int : bool = False

    def evaluate_node(self, prog : Program) -> IREvaluation:
        return Conjunction(self.var.get_type().restrict(self.var), self.pred).evaluate(prog).with_ref(self.var)

    def transform(self, transformer : IRTransformer) -> PredicateExpr:
        return transformer.transform_PredicateExpr(self)

    def __str__(self) -> str:
        return self.format_type('Expr({}, {})'.format(self.var, self.pred))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.var == other.var and self.pred == other.pred

    def __hash__(self) -> int:
        return hash((self.var, self.pred))
