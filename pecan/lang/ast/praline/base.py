
from pecan.lang.ast.base import ASTNode

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast.praline.match import PralineMatchPat

class PralineASTNode(ASTNode):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        raise NotImplementedError # We force every PralineIRNode to have a canonical string representation
    
    def __repr__(self) -> str:
        return self.__str__() # Fallback for list printing

class PralineTerm(PralineASTNode):
    var_counter = 0
    @staticmethod
    def fresh_name() -> str:
        label = "__arg{}".format(PralineTerm.var_counter)
        PralineTerm.var_counter += 1
        return label

    def __init__(self):
        super().__init__()

    def build_match(self) -> PralineMatchPat:
        raise NotImplementedError

class PralineBinaryOp(PralineTerm):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__()
        self.a : PralineTerm = a
        self.b : PralineTerm = b

class PralineUnaryOp(PralineTerm):
    def __init__(self, a : PralineTerm):
        super().__init__()
        self.a : PralineTerm = a
