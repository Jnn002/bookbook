from abc import ABC, abstractmethod
from typing import Any, Optional

from src.application.dtos.external_book_dtos import (
    ExternalBookItemDTO,
    ExternalBookSearchResponseDTO,
)


class ExternalBookServicePort(ABC):
    """Interface for external book service communication."""

    @abstractmethod
    async def search_books(
        self,
        query: str,
        filters: Optional[dict[str, Any]] = None,
        page_index: int = 0,
        page_size: int = 10,
    ) -> ExternalBookSearchResponseDTO:
        """
        Search for books using the external book service.

        :param query: The search query string.
        :param filters: Optional filters to apply to the search.
        :param page_index: The index of the page to retrieve (for pagination).
        :param page_size: The number of items per page.
        :return: A response object containing the search results.
        """
        pass

    @abstractmethod
    async def get_book_details_by_external_id(
        self, external_id: str
    ) -> Optional[ExternalBookItemDTO]:
        """
        Retrieve book details by external ID.

        :param external_id: The external ID of the book.
        :return: A response object containing the book details.
        """
        pass
