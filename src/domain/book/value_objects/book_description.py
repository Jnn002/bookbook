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

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyDescription('Book - Description cannot be empty')
        if len(self.value) > 1000:
            raise InvalidDescriptionLength(
                'Book - Description cannot exceed 1000 characters'
            )

    def __str__(self) -> str:
        return self.value
