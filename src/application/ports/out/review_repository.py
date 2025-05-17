import uuid
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.review.review import DomainReview


class ReviewRepository(ABC):
    @abstractmethod
    async def save_review(self, review: DomainReview) -> DomainReview:
        """
        Save a review to the repository.

        :param review: An instance of DomainReview to save.
        :return: The saved instance of DomainReview.
        """
        pass

    @abstractmethod
    async def delete_review(self, review_id: uuid.UUID) -> None:
        """
        Delete a review from the repository by its ID.

        :param review_id: The ID of the review to delete.
        """
        pass

    @abstractmethod
    async def get_review_by_id(self, review_id: uuid.UUID) -> Optional[DomainReview]:
        """
        Retrieve a review by its ID.

        :param review_id: The ID of the review to retrieve.
        :return: An instance of DomainReview if found, otherwise None.
        """
        pass

    @abstractmethod
    async def get_reviews_by_user_id(
        self, user_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> list[DomainReview]:
        """
        Retrieve all reviews by a specific user.

        :param user_id: The ID of the user whose reviews to retrieve.
        :return: A list of DomainReview instances.
        """
        pass

    @abstractmethod
    async def get_reviews_by_book_id(
        self, book_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> list[DomainReview]:
        """
        Retrieve all reviews for a specific book.

        :param book_id: The ID of the book whose reviews to retrieve.
        :return: A list of DomainReview instances.
        """
        pass

    @abstractmethod
    async def get_review_by_user_and_book_id(
        self, user_id: uuid.UUID, book_id: uuid.UUID
    ) -> Optional[DomainReview]:
        """
        Retrieve a review by a specific user for a specific book.

        :param user_id: The ID of the user who wrote the review.
        :param book_id: The ID of the book being reviewed.
        :return: An instance of DomainReview if found, otherwise None.
        """
        pass
