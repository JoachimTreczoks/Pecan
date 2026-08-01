
from pecan.lang.ast.praline.base import PralineTerm
from pecan.lang.ast.praline.match import PralineMatchVar, PralineMatchInt, PralineMatchString, PralineMatchTuple, PralineMatchList

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from pecan.lang.ast_transformer import AstTransformer

class PralineValueHolder(PralineTerm):
    pass

class PralineVar(PralineValueHolder):
    def __init__(self, var_name : str):
        super().__init__()
        self.var_name : str = var_name

    def transform(self, transformer : AstTransformer) -> PralineVar:
        return transformer.transform_PralineVar(self)

    def build_match(self) -> PralineMatchVar:
        return PralineMatchVar(self.var_name)

    def __str__(self) -> str:
        return '{}'.format(self.var_name)

class PralineInt(PralineValueHolder):
    def __init__(self, val : int):
        super().__init__()
        self.val : int = val

    def transform(self, transformer : AstTransformer) -> PralineInt:
        return transformer.transform_PralineInt(self)

    def build_match(self) -> PralineMatchInt:
        return PralineMatchInt(self.val)

    def __str__(self) -> str:
        return '{}'.format(self.val)
    
    def __repr__(self) -> str:
        return 'PralineInt({})'.format(self.val)

class PralineString(PralineValueHolder):
    def __init__(self, val : str):
        super().__init__()
        self.val : str = val

    def transform(self, transformer : AstTransformer) -> PralineString:
        return transformer.transform_PralineString(self)

    def build_match(self) -> PralineMatchString:
        return PralineMatchString(self.val)

    def __str__(self) -> str:
        return self.val

    def __repr__(self) -> str:
        return 'PralineString({})'.format(self.val)

class PralineBool(PralineValueHolder):
    def __init__(self, val : bool):
        super().__init__()
        self.val : bool = val

    def transform(self, transformer : AstTransformer) -> PralineBool:
        return transformer.transform_PralineBool(self)

    def __str__(self) -> str:
        if self.val:
            return 'true'
        else:
            return 'false'

    def __repr__(self) -> str:
        return 'PralineBool({})'.format(self.val)

class PralineTuple(PralineValueHolder):
    def __init__(self, vals : list[PralineTerm]):
        super().__init__()
        self.vals : list[PralineTerm] = vals

    def build_match(self) -> PralineMatchTuple:
        return PralineMatchTuple([v.build_match() for v in self.vals])

    def transform(self, transformer : AstTransformer) -> PralineTuple:
        return transformer.transform_PralineTuple(self)

    def __str__(self) -> str:
        return '({})'.format(', '.join(map(str, self.vals)))

    def __repr__(self) -> str:
        return '({})'.format(', '.join(map(repr, self.vals)))

class PralineList(PralineValueHolder):
    def __init__(self, head : PralineTerm | None, tail : PralineTerm | None):
        super().__init__()
        self.head : PralineTerm | None = head
        self.tail : PralineTerm | None = tail

    def transform(self, transformer : AstTransformer) -> PralineList:
        return transformer.transform_PralineList(self)

    def build_match(self) -> PralineMatchList:
        assert self.head is not None and self.tail is not None
        return PralineMatchList(self.head.build_match(), self.tail.build_match())

    def __str__(self) -> str:
        elems = []
        cur : PralineList = self

        while cur.head is not None:
            elems.append(cur.head)
            assert isinstance(cur.tail, PralineList)
            cur = cur.tail

        return '[{}]'.format(', '.join([str(e) for e in elems]))

    def __repr__(self) -> str:
        if self.tail is None:
            return '[]'
        else:
            return '({} :: {})'.format(self.head, self.tail)
