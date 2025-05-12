class ReviewDomainException(Exception):
    """Base class for all review exceptions."""

    pass


class EmptyReview(ReviewDomainException):
    """Review text cannot be empty."""

    pass


class LengthExceeded(ReviewDomainException):
    """Review text exceeds maximum length. (500 characters)."""

    pass


class InvalidRating(ReviewDomainException):
    """Rating must be between 1 and 5."""

    pass
