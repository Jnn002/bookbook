import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.book.book import DomainBook
from src.domain.book.value_objects.book_isbn import IsbnVO


class BookRepository(ABC):
    @abstractmethod
    async def get_book_by_id(self, book_id: uuid.UUID) -> Optional[DomainBook]:
        """
        Retrieve a book by its ID.

        :param book_id: The UUID of the book to retrieve.
        :return: An instance of DomainBook if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_book_by_google_id(self, google_book_id: str) -> Optional[DomainBook]:
        """
        Retrieve a book by its Google ID.

        :param google_book_id: The Google ID of the book to retrieve.
        :return: An instance of DomainBook if found, otherwise None.
        """
        pass

    @abstractmethod
    async def save_book(self, book: DomainBook) -> DomainBook:
        """
        Save a book to the repository.

        :param book: An instance of DomainBook to save.
        :return: The saved instance of DomainBook.
        """
        pass

    # TODO: Evaluate that there is no review associated with the book
    @abstractmethod
    async def delete_book(self, book_id: uuid.UUID) -> None:
        """
        Delete a book from the repository by its ID.

        :param book_id: The UUID of the book to delete.
        """
        pass

    @abstractmethod
    async def get_all_books(self, limit: int = 10, offset: int = 0) -> list[DomainBook]:
        """
        Retrieve all books from the repository with pagination.

        :param limit: The maximum number of books to retrieve.
        :param offset: The number of books to skip before starting to collect the result set.
        :return: A list of DomainBook instances.
        """
        pass

    @abstractmethod
    async def get_book_by_isbn(self, isbn: IsbnVO) -> Optional[DomainBook]:
        """
        Retrieve a book by its ISBN.

        :param isbn: The ISBN of the book to retrieve.
        :return: An instance of DomainBook if found, otherwise None.
        """
        pass
