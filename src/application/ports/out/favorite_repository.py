import uuid
from abc import ABC, abstractmethod
from typing import List

from src.domain.book.book import DomainBook


class FavoriteRepository(ABC):
    """
    Port defining operations for managing user's favorite books.
    """

    @abstractmethod
    async def add_favorite(self, user_id: uuid.UUID, book_id: uuid.UUID) -> None:
        """Marks a book as a favorite for a user."""
        pass

    @abstractmethod
    async def remove_favorite(self, user_id: uuid.UUID, book_id: uuid.UUID) -> bool:
        """Removes a book from a user's favorites. Returns True if removed."""
        pass

    @abstractmethod
    async def is_book_favorited_by_user(
        self, user_id: uuid.UUID, book_id: uuid.UUID
    ) -> bool:
        """Checks if a specific book is favorited by a specific user."""
        pass

    @abstractmethod
    async def list_favorite_books_by_user(
        self, user_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> List[DomainBook]:
        """
        Lists all books marked as favorite by a specific user, with pagination.
        """
        pass

    # TODO: check for this method later
    # @abstractmethod
    # async def count_favorites_for_book(self, book_id: uuid.UUID) -> int:
    #    """Counts how many users have favorited a specific book."""
    #    pass
