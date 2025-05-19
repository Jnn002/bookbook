class BookDomainException(Exception):
    """Base class for all book domain exceptions."""

    pass


class EmptyTitle(BookDomainException):
    """Title cannot be empty"""

    pass


class EmptySubtitle(BookDomainException):
    """Subtitle cannot be empty"""

    pass


class EmptyDescription(BookDomainException):
    """Description cannot be empty"""

    pass


class InvalidDescriptionLength(BookDomainException):
    """Description cannot exceed 1000 characters"""

    pass


class EmptyAuthors(BookDomainException):
    """Authors cannot be empty"""

    pass


class EmptyPublisher(BookDomainException):
    """Publisher cannot be empty"""

    pass


class EmptyLanguage(BookDomainException):
    """Language cannot be empty"""

    pass


class InvalidPageCount(BookDomainException):
    """Page count must be greater than 0"""

    pass


class InvalidPublishedDate(BookDomainException):
    """Published date cannot be in the future"""

    pass


class EmptyGoogleBookId(BookDomainException):
    """Google Book ID cannot be empty"""

    pass


class EmptyIsbn(BookDomainException):
    """ISBN cannot be empty"""

    pass


class EmptyCoverImageUrl(BookDomainException):
    """Cover image URL cannot be empty"""

    pass


class BookNotFound(BookDomainException):
    """Book not found"""

    pass
