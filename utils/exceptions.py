class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class UniqueConstraintError(ValidationError):
    """Raised when unique constraint is violated"""
    pass

class NotFoundError(Exception):
    """Raised when requested resource is not found"""
    pass

class ConstraintError(Exception):
    """Raised when business constraint is violated"""
    pass

class StorageError(Exception):
    """Raised when storage operation fails"""
    pass