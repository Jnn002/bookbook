import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.tag.tags import DomainTag


class TagRepository(ABC):
    """
    Port for managing global Tag entities and their associations with Books.
    """

    @abstractmethod
    async def get_or_create_tag_by_name(self, name: str) -> DomainTag:
        """
        Retrieves a tag by its unique name. If it doesn't exist, it creates it.
        The name should be normalized (e.g., lowercase, trimmed) before calling this.
        Returns the existing or newly created DomainTag.
        """
        pass

    @abstractmethod
    async def get_tag_by_id(self, tag_id: uuid.UUID) -> Optional[DomainTag]:
        """Retrieves a tag by its ID."""
        pass

    @abstractmethod
    async def list_all_tags(self, limit: int = 100, offset: int = 0) -> list[DomainTag]:
        """Lists all globally available tags, with pagination."""
        pass

    @abstractmethod
    async def link_tag_to_book(self, book_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        """Creates an association between a book and a tag."""
        pass

    @abstractmethod
    async def unlink_tag_from_book(self, book_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        """Removes an association between a book and a tag."""
        pass

    @abstractmethod
    async def unlink_all_tags_from_book(self, book_id: uuid.UUID) -> None:
        """Removes all tag associations for a given book. Useful if categories change."""
        pass

    @abstractmethod
    async def get_tags_for_book(self, book_id: uuid.UUID) -> list[DomainTag]:
        """Retrieves all tags associated with a specific locally registered book."""
        pass
