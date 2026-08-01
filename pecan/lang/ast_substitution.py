#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast import *

from pecan.lang.ast_transformer import AstTransformer

class ASTSubstitution(AstTransformer):
    def __init__(self, subs : dict[str, VarRef]):
        super().__init__()
        self.subs : dict[str, VarRef] = subs

    def transform_str(self, original_str : str) -> str | VarRef:
        return self.subs.get(original_str, original_str)

    def transform_VarRef(self, node : VarRef) -> VarRef:
        return self.subs.get(node.var_name, node)

