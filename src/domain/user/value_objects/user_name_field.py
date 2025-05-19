import re
from dataclasses import dataclass

from src.domain.exceptions.user_exceptions import EmptyFieldName, InvalidFieldName


@dataclass(frozen=True)
class FieldName:
    """
    Represents a field name as a Value Object.

    Attributes:
        value (str): The field name.

    Raises:
        EmptyFieldName: If the field name is empty or contains only whitespace.
        InvalidFieldName: If the field name contains invalid characters.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise EmptyFieldName('User - Field name cannot be empty')

        field_name_regex = r'^[A-Za-z\s]+$'
        if not re.fullmatch(field_name_regex, self.value):
            raise InvalidFieldName('User - Field name must contain only letters')

    def __str__(self) -> str:
        return self.value
