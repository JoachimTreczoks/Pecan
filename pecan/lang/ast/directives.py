#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast.base import ASTNode
from pecan.lang.ast.prog import VarRef, Call

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Literal
    from pecan.lang.ast_transformer import AstTransformer

class DirectiveSaveAut(ASTNode):
    def __init__(self, filename : str, pred_name : str):
        super().__init__()
        self.filename : str = filename
        self.pred_name : str = pred_name

    def transform(self, transformer : AstTransformer) -> DirectiveSaveAut:
        return transformer.transform_DirectiveSaveAut(self)

    def __repr__(self) -> str:
        return '#save_aut({}, {})'.format(self.filename, self.pred_name)

class DirectiveSaveAutImage(ASTNode):
    def __init__(self, filename : str, pred_name : str):
        super().__init__()
        self.filename : str = filename
        self.pred_name : str = pred_name

    def transform(self, transformer : AstTransformer) -> DirectiveSaveAutImage:
        return transformer.transform_DirectiveSaveAutImage(self)

    def __repr__(self) -> str:
        return '#save_aut_img({}, {})'.format(self.filename, self.pred_name)

class DirectiveContext(ASTNode):
    def __init__(self, context_key : str, context_val : str):
        super().__init__()
        self.context_key : str= context_key
        self.context_val : str = context_val

    def transform(self, transformer : AstTransformer) -> DirectiveContext:
        return transformer.transform_DirectiveContext(self)

    def __repr__(self) -> str:
        return '#context({}, {})'.format(self.context_key, self.context_val)

class DirectiveEndContext(ASTNode):
    def __init__(self, context_key : str):
        super().__init__()
        self.context_key : str = context_key

    def transform(self, transformer : AstTransformer) -> DirectiveEndContext:
        return transformer.transform_DirectiveEndContext(self)

    def __repr__(self) -> str:
        return '#end_context({})'.format(self.context_key)

# Asserts that pred_name is truth_val: i.e., that pred_name is 'true' (always), 'false' (always), or 'sometimes' true
class DirectiveAssertProp(ASTNode):
    def __init__(self, truth_val : Literal['false', 'true', 'sometimes'], pred_name : str):
        super().__init__()
        self.truth_val : Literal['false', 'true', 'sometimes'] = truth_val
        self.pred_name : str = pred_name

    def transform(self, transformer : AstTransformer) -> DirectiveAssertProp:
        return transformer.transform_DirectiveAssertProp(self)

    def __repr__(self) -> str:
        return '#assert_prop({}, {})'.format(self.truth_val, self.pred_name)

class DirectiveLoadAut(ASTNode):
    def __init__(self, filename : str, aut_format : str, pred : VarRef | Call):
        super().__init__()
        self.filename : str = filename
        self.aut_format : str = aut_format
        self.pred : VarRef | Call = pred

    def transform(self, transformer : AstTransformer) -> DirectiveLoadAut:
        return transformer.transform_DirectiveLoadAut(self)

    def __repr__(self) -> str:
        return '#load("{}", "{}", {})'.format(self.filename, self.aut_format, repr(self.pred))

class DirectiveImport(ASTNode):
    def __init__(self, filename : str):
        super().__init__()
        self.filename : str = filename

    def transform(self, transformer : AstTransformer) -> DirectiveImport:
        return transformer.transform_DirectiveImport(self)

    def __repr__(self) -> str:
        return '#import({})'.format(self.filename)

class DirectiveForget(ASTNode):
    def __init__(self, var_name : str):
        super().__init__()
        self.var_name : str = var_name

    def transform(self, transformer : AstTransformer) -> DirectiveForget:
        return transformer.transform_DirectiveForget(self)

    def __repr__(self) -> str:
        return '#forget({})'.format(self.var_name)

class DirectiveStructure(ASTNode):
    def __init__(self, pred_ref : VarRef | Call, val_dict : dict[str, Call]):
        super().__init__()

        if type(pred_ref) is VarRef:
            self.pred_ref : Call = Call(pred_ref.var_name, [VarRef('*')])
        elif type(pred_ref) is Call:
            self.pred_ref : Call = pred_ref.add_arg(VarRef('*'))
        else:
            raise Exception('Pred ref {} is not a VarRef or Call'.format(pred_ref))

        self.val_dict : dict[str, Call] = val_dict

    def transform(self, transformer : AstTransformer) -> DirectiveStructure:
        return transformer.transform_DirectiveStructure(self)

    def __repr__(self) -> str:
        return 'Structure {} defining {} .'.format(self.pred_ref, self.val_dict)

class DirectiveShuffle(ASTNode):
    def __init__(self, disjunction : bool, pred_a : Call, pred_b : Call, output_pred : Call): # TODO: If the predicates are 0-ary they are `VarRef`s instead of `Call`s, leading to an exception
        super().__init__()
        self.disjunction : bool = disjunction
        self.pred_a : Call = pred_a
        self.pred_b : Call = pred_b
        self.output_pred : Call = output_pred

    def transform(self, transformer : AstTransformer) -> DirectiveShuffle:
        return transformer.transform_DirectiveShuffle(self)

    def __repr__(self) -> str:
        return '#shuffle({}, {}, {})'.format(self.pred_a, self.pred_b, self.output_pred)

