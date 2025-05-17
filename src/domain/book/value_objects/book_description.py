from dataclasses import dataclass

from src.domain.exceptions.book_exceptions import (
    EmptyDescription,
    InvalidDescriptionLength,
)


@dataclass(frozen=True)
class BookDescription:
    """
    BookDescription is a value object that represents the description of a book.
    """

    description: str

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise EmptyDescription('Book - Description cannot be empty')
        if len(self.description) > 1000:
            raise InvalidDescriptionLength(
                'Book - Description cannot exceed 1000 characters'
            )

    def __str__(self) -> str:
        return self.description
