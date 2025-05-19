from dataclasses import dataclass

from src.domain.exceptions.book_exceptions import EmptySubtitle


@dataclass
class BookSubtitle:
    """
    BookSubtitle is a value object that represents the subtitle of a book.
    """

    subtitle: str

    def __post_init__(self) -> None:
        if not self.subtitle or not self.subtitle.strip():
            raise EmptySubtitle('Book - Subtitle cannot be empty')
        # TODO: Manange default value on the adapter

    def __str__(self) -> str:
        return self.subtitle
