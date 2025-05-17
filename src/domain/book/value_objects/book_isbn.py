from dataclasses import dataclass

from src.domain.exceptions.book_exceptions import EmptyIsbn


@dataclass(frozen=True)
class IsbnVO:
    """Value Object for ISBN."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyIsbn('ISBN cannot be empty')

    def __str__(self) -> str:
        return self.value
