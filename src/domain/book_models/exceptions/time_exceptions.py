class TimeDomainException(Exception):
    """Base class for all time-related exceptions."""

    pass


class FutureCreatedAtError(TimeDomainException):
    """Created at cannot be in the future"""

    pass


class UpdatedBeforeCreatedError(TimeDomainException):
    """Updated at must be greater than or equal to created at"""

    pass


class NaiveDateTimeError(TimeDomainException):
    """Datetime must be timezone-aware"""

    pass
