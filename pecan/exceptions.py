
class PlottingError(Exception):
    """Raised when something prevents successful plotting"""
    pass

class PralineConversionError(Exception):
    """Raised when Praline fails to convert a given value"""
    pass

class PralineLogicError(Exception):
    """Raised when something breaks the internal logic of Praline"""
    pass

class PralineTypeError(TypeError):
    """Raised when a Praline method is called with arguments of incorrect type"""
    pass

class AutomatonReadingError(Exception):
    """Raised when issues arise related to reading Automatons from files"""
    pass

class AutomatonArithmeticError(ArithmeticError):
    """Raised when a trying to execute invalid arithmetic operations for Automatons"""
    pass

class CallResolvingError(Exception):
    """Raised when anything related to resolving a Call fails"""
    pass

class MatchingError(Exception):
    """Raised when a Match statement can't be resolved"""
    pass

class UnificationError(Exception):
    """Raised when the unification of types fails"""
    pass
