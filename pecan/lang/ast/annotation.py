#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast.base import Predicate

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer;

class Annotation(Predicate):
    def __init__(self, annotation_name : str, body : Predicate):
        super().__init__()
        self.annotation_name : str = annotation_name
        self.body : Predicate = body

    def transform(self, transformer : AstTransformer) -> Annotation:
        return transformer.transform_Annotation(self)

    def __repr__(self) -> str:
        return '{}[{}]'.format(self.annotation_name, self.body)

