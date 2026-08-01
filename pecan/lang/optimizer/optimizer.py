#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.optimizer.boolean import BooleanOptimizer
from pecan.lang.optimizer.arithmetic import ArithmeticOptimizer
from pecan.lang.optimizer.cse import CSEOptimizer
from pecan.lang.optimizer.redundant_variable_optimizer import RedundantVariableOptimizer
from pecan.lang.optimizer.unused_variable_optimizer import UnusedVariableOptimizer
from pecan.lang.ir import *

from pecan.settings import settings
from pecan.logger import Logger

class UntypedOptimizer:
    def __init__(self, prog : Program):
        self.prog = prog

    def optimize(self) -> Program:
        for i, d in enumerate(self.prog.defs):
            if isinstance(d, NamedPred):
                self.prog.defs[i] = NamedPred(d.name, d.args, d.arg_restrictions, self.run_optimizations(d.body, d), restriction_env=d.restriction_env, arg_name_map=d.arg_name_map)

        return self.prog

    def run_optimizations(self, node, pred):
        Logger.log('Optimizing: {}'.format(node), 2)

        if settings.min_opt():
            optimization_pass = [ ArithmeticOptimizer(self), BooleanOptimizer(self) ]
        else:
            optimization_pass = [ ArithmeticOptimizer(self), BooleanOptimizer(self) ] # RedundantVariableOptimizer(self) ]

        Logger.log('Optimization passes: [{}]'.format(', '.join(map(str, (optimization_pass)))), 2)

        new_node = node

        ast_changed = True # Default to true so we run at least once
        while ast_changed:
            ast_changed = False
            for optimization in optimization_pass:
                changed, new_node = optimization.optimize(new_node, pred)
                ast_changed |= changed

        Logger.log('Optimized node: {}'.format(new_node), 2)

        return new_node

class Optimizer:
    def __init__(self, prog : Program):
        self.prog = prog

    def optimize(self, pred) -> NamedPred:
        return NamedPred(pred.name, pred.args, pred.arg_restrictions, self.run_optimizations(pred.body, pred), restriction_env=pred.restriction_env, arg_name_map=pred.arg_name_map)

    def run_optimizations(self, node : IRNode, pred):
        Logger.log('Optimizing: {}'.format(node), 2)

        if settings.min_opt():
            optimization_pass = [ ArithmeticOptimizer(self), BooleanOptimizer(self) ]
        else:
            # optimization_pass = [ ArithmeticOptimizer(self), CSEOptimizer(self), BooleanOptimizer(self), RedundantVariableOptimizer(self), UnusedVariableOptimizer(self) ]
            optimization_pass = [ ArithmeticOptimizer(self), CSEOptimizer(self), BooleanOptimizer(self), UnusedVariableOptimizer(self) ]

        Logger.log('Optimization passes: [{}]'.format(', '.join(map(str, (optimization_pass)))), 2)

        new_node = node

        ast_changed = True # Default to true so we run at least once
        while ast_changed:
            ast_changed = False
            for optimization in optimization_pass:
                changed, new_node = optimization.optimize(new_node, pred)
                ast_changed |= changed

        Logger.log('Optimized node: {}'.format(new_node), 2)

        return new_node

