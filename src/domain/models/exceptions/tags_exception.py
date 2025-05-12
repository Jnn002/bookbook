class TagsDomainException(Exception):
    """Base class for exceptions in the tags domain."""

    pass


class EmptyName(TagsDomainException):
    """Name of the tag cannot be empty"""

    pass


class NameTooLong(TagsDomainException):
    """Name of the tag cannot be longer than 20 characters"""

    pass
