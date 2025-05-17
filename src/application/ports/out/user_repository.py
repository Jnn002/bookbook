import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.user.user import DomainUser
from src.domain.user.value_objects.user_email import UserEmailVO


class UserRepository(ABC):
    @abstractmethod
    async def save_user(self, user: DomainUser) -> DomainUser:
        """
        Save a user to the repository.
        """
        pass

    @abstractmethod
    async def delete_user(self, user_id: uuid.UUID) -> None:
        """
        Delete a user from the repository.
        """
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[DomainUser]:
        """
        Retrieve a user by their ID.
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: UserEmailVO) -> Optional[DomainUser]:
        """
        Retrieve a user by their email.
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: UserEmailVO) -> bool:
        """
        Check if a user exists by their email.
        """
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists by their username.
        """
        pass
