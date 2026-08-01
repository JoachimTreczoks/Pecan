
from pecan.lang.ir.base import IRNode

from pecan.lang.ir.prog import Program
from pecan.tools.labeled_aut_converter import *

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any, Literal

class PralineIRNode(IRNode):
    def __init__(self):
        super().__init__()
    
    def evaluate(self, prog: Program) -> PralineTerm:
        return PralineDummy()

    def __str__(self) -> str:
        raise NotImplementedError # We force every PralineIRNode to have a canonical string representation
    
    def __repr__(self) -> str:
        return self.__str__() # Fallback for list printing

class PralineTerm(PralineIRNode):
    def __init__(self, value_type : Literal['bool', 'int', 'string', 'unknown'] = 'unknown'):
        super().__init__()
        self.value_type : Literal['bool', 'int', 'string', 'unknown'] = value_type

    # If an `is_X()` method returns true, the corresponding `get_X()` method should be implemented!
    def is_bool(self) -> bool:
        return self.value_type == 'bool'

    def is_int(self) -> bool:
        return self.value_type == 'int'

    def is_string(self) -> bool:
        return self.value_type == 'string'
    
    def get_bool(self) -> bool:
        raise NotImplementedError
    
    def get_int(self) -> int:
        raise NotImplementedError
    
    def get_string(self) -> str:
        raise NotImplementedError

class PralineDummy(PralineTerm):
    """
    Dummy class for making PralineTerms non-optional
    """
    def __init__(self):
        super().__init__()

    def match(self, term : PralineTerm, prog : Program) -> dict | None: # For using the PralineDummy instead of PralineMatchPat objects
        raise NotImplementedError
    
    def __str__(self) -> str:
        return '<Empty>'
    
    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__)

class PralineBinaryOp(PralineTerm):
    def __init__(self, a : PralineTerm, b : PralineTerm):
        super().__init__()
        self.a : PralineTerm = a
        self.b : PralineTerm = b

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a and self.b == other.b

    def __hash__(self) -> int:
        return hash((self.a, self.b))

class PralineUnaryOp(PralineTerm):
    def __init__(self, a : PralineTerm):
        super().__init__()
        self.a : PralineTerm = a

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.a == other.a

    def __hash__(self) -> int:
        return hash(self.a)
