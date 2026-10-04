class PlatformError(Exception):
    """Base class for expected application errors."""


class AuthenticationError(PlatformError):
    """Raised when authentication data cannot be verified."""


class AuthorizationError(PlatformError):
    """Raised when a caller lacks the required permission."""


class NotFoundError(PlatformError):
    """Raised when a requested domain object does not exist."""


class ValidationError(PlatformError):
    """Raised for domain-level input validation failures."""
