#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ir_transformer import IRTransformer
from pecan.logger import Logger

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ir.base import IRNode
    from pecan.lang.optimizer.optimizer import Optimizer

class BasicOptimizer(IRTransformer):
    def __init__(self, master_optimizer : Optimizer):
        super().__init__()
        self.changed : bool = False
        self.master_optimizer : Optimizer = master_optimizer
        self.prog = master_optimizer.prog
        self.pred = None

    def pre_optimize(self, node : IRNode):
        pass

    def post_optimize(self, node : IRNode):
        pass

    def optimize(self, node : IRNode, pred) -> tuple[bool, IRNode]:
        self.changed = False

        self.pred = pred

        Logger.log('Before pre-optimize {}: {}'.format(type(self).__name__, node), 3)
        res = self.pre_optimize(node)
        if res is not None:
            node = res

        if self.changed:
            Logger.log('Before optimize {}: {}'.format(type(self).__name__, node), 3)

        new_node = self.transform(node)

        if self.changed:
            Logger.log('Before post-optimize {}: {}'.format(type(self).__name__, new_node), 3)

        res = self.post_optimize(new_node)
        if res is not None:
            new_node = res

        if self.changed:
            Logger.log('After post-optimize {}: {}'.format(type(self).__name__, new_node), 3)

        return self.changed, new_node

    def __str__(self) -> str:
        return 'BasicOptimizer'
