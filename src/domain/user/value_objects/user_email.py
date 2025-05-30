import re
from dataclasses import dataclass

from src.domain.exceptions.user_exceptions import InvalidEmail


@dataclass(frozen=True)
class UserEmailVO:
    """
    Represents a user's email address as a Value Object.

    Attributes:
        value (str): The email address.

    Raises:
        InvalidEmail: If the email format is invalid.
    """

    value: str

    def __post_init__(self):
        """Validates the email format after initialization."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.fullmatch(email_regex, self.value):
            raise InvalidEmail(f'Invalid email format: {self.value}')

    def __str__(self) -> str:
        """Returns the string representation of the email."""
        return self.value

    @property
    def domain(self) -> str:
        """Extracts the domain from the email address."""
        return self.value.split('@')[1]
