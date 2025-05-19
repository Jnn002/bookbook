from dataclasses import dataclass

from src.domain.exceptions.book_exceptions import InvalidPageCount


@dataclass(frozen=True)
class BookPageCount:
    """
    PageCount is a value object that represents the page count of a book.
    """

    page_count: int

    def __post_init__(self) -> None:
        if self.page_count <= 0:
            raise InvalidPageCount('Book - Page count must be greater than 0')

    def __str__(self) -> str:
        return str(self.page_count)
