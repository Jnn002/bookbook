class UserDomainException(Exception):
    """Base class for user domain exceptions."""

    pass


class EmptyUsername(UserDomainException):
    """Username cannot be empty"""

    pass


class EmptyFirstName(UserDomainException):
    """First name cannot be empty"""

    pass


class EmptyLastName(UserDomainException):
    """Last name cannot be empty"""

    pass


class InvalidEmail(UserDomainException):
    """Invalid email address"""

    pass


class InvalidHashedPassword(UserDomainException):
    """Invalid hashed password"""

    pass
