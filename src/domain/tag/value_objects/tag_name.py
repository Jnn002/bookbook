from dataclasses import dataclass

from src.domain.exceptions.tags_exception import EmptyName, NameTooLong


@dataclass(frozen=True)
class TagNameVO:
    """
    Value Object representing the name of a tag.
    Ensures the tag name is not empty and adheres to length constraints.
    """

    value: str
    MAX_LENGTH: int = 50

    def __post_init__(self) -> None:
        """Validate the tag name."""
        if not isinstance(self.value, str) or not self.value.strip():
            raise EmptyName('Tag name cannot be empty.')
        if len(self.value) > self.MAX_LENGTH:
            raise NameTooLong(f'Tag name cannot exceed {self.MAX_LENGTH} characters.')

    def __str__(self) -> str:
        return self.value.strip().lower()
