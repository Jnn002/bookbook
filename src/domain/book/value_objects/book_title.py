from dataclasses import dataclass

from src.domain.exceptions.book_exceptions import EmptyTitle


@dataclass(frozen=True)
class BookTitle:
    """
    BookTitle is a value object that represents the title of a book.
    """

    title: str

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise EmptyTitle('Book - Title cannot be empty')

    def __str__(self) -> str:
        return self.title
