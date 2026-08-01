#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ir import *

from pecan.settings import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.ir.base import IREvaluation, IRNode, IRPredicate
    from pecan.lang.ir.prog import Program

class Annotation(IRPredicate):
    def __init__(self, annotation_name : str, body : IRNode):
        super().__init__()
        self.annotation_name : str = annotation_name
        self.body : IRNode = body

    def evaluate_node(self, prog : Program) -> IREvaluation:
        if self.annotation_name == '@no_simplify':
            orig_level = settings.get_simplification_level()
            settings.set_simplification_level(0)
            res = self.body.evaluate(prog)
            settings.set_simplification_level(orig_level)
            return res
        elif self.annotation_name == '@simplify':
            orig_level = settings.get_simplification_level()
            settings.set_simplification_level(1)
            res = self.body.evaluate(prog)
            settings.set_simplification_level(orig_level)
            return res
        elif self.annotation_name == '@simplify_high':
            orig_level = settings.get_simplification_level()
            settings.set_simplification_level(2)
            res = self.body.evaluate(prog)
            settings.set_simplification_level(orig_level)
            return res
        elif self.annotation_name == '@postprocess':
            return self.body.evaluate(prog).postprocess()
        elif self.annotation_name == '@postprocess_high':
            return self.body.evaluate(prog).postprocess(level='High')
        elif self.annotation_name == '@postprocess_medium':
            return self.body.evaluate(prog).postprocess(level='Medium')
        elif self.annotation_name == '@postprocess_low':
            return self.body.evaluate(prog).postprocess(level='Low')
        elif self.annotation_name == '@simplify_states':
            return self.body.evaluate(prog).simplify_states()
        elif self.annotation_name == '@simplify_edges':
            return self.body.evaluate(prog).simplify_edges()
        elif self.annotation_name == '@merge_states':
            return self.body.evaluate(prog).merge_states()
        elif self.annotation_name == '@merge_edges':
            return self.body.evaluate(prog).merge_edges()
        elif self.annotation_name == '@merge_states_loop':
            evaluation = self.body.evaluate(prog)
            n = evaluation.num_states() + 1
            while evaluation.num_states() < n:
                n = evaluation.num_states()
                evaluation.merge_states()
            return evaluation
        else:
            raise ValueError('Unknown annotation: {}'.format(self.annotation_name))

    def transform(self, transformer : IRTransformer) -> Annotation:
        return transformer.transform_Annotation(self)

    def __str__(self) -> str:
        return '{}[{}]'.format(self.annotation_name, self.body)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.annotation_name == other.annotation_name and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.annotation_name, self.body))

