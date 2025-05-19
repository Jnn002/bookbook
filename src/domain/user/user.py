"""Module for the User domain entity."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.exceptions.time_exceptions import NaiveDateTimeError
from src.domain.exceptions.user_exceptions import (
    EmptyFieldName,
    EmptyUsername,
    InvalidEmail,
    InvalidHashedPassword,
)
from src.domain.user.value_objects.user_email import UserEmailVO
from src.domain.user.value_objects.user_name_field import FieldName


@dataclass
class DomainUser:
    """
    Represents the domain entity for a User.

    Attributes:
        id (UUID): Unique identifier for the user.
        username (str): Unique username for the user.
        email (UserEmailVO): User's email address.
        first_name (FieldName): User's first name.
        last_name (FieldName): User's last name.
        hashed_password (str): User's hashed password.
        created_at (datetime): Timestamp of when the user was created.
        updated_at (datetime): Timestamp of the user's last update.
        is_verified (bool): Indicates if the user is verified.
    """

    id: uuid.UUID
    username: str
    email: UserEmailVO
    first_name: FieldName
    last_name: FieldName
    hashed_password: str
    updated_at: datetime
    created_at: datetime
    is_verified: bool = False

    def __post_init__(self) -> None:
        """
        Validates attributes after initialization.

        Raises:
            ValueError: If any attribute does not meet the required conditions.
        """
        if not self.username or not self.username.strip():
            raise EmptyUsername('User - Username cannot be empty')
        if not self.first_name:
            raise EmptyFieldName('User - First name cannot be empty')
        if not self.last_name:
            raise EmptyFieldName('User - Last name cannot be empty')
        if not self.email or not isinstance(self.email, UserEmailVO):
            raise InvalidEmail('User - Invalid email address')
        if not self.hashed_password or not isinstance(self.hashed_password, str):
            raise InvalidHashedPassword('User - Invalid hashed password')
        if self.created_at.tzinfo is None:
            raise NaiveDateTimeError('User - Created at must be timezone-aware')
        if self.updated_at.tzinfo is None:
            raise NaiveDateTimeError('User - Updated at must be timezone-aware')

    def verify(self) -> None:
        """
        Marks the user as verified.

        Raises:
            ValueError: If the user is already verified.
        """
        if self.is_verified:
            raise ValueError('User - User is already verified')
        self.is_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def change_password(self, new_hashed_password: str) -> None:
        """
        Changes the user's password.

        Args:
            new_hashed_password (str):
                The new hashed password.
                The hashing logic should be outside
                the domain entity.
        """
        # * Password strength validation is not performed here;
        # * it should occur before hashing and passing it to this method. app and infrastructure layers
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.now(timezone.utc)
