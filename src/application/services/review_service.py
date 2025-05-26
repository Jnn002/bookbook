import uuid
from datetime import datetime, timezone
from typing import List, Optional

from src.application.ports.out.book_repository import BookRepository

# --- Puertos ---
from src.application.ports.out.review_repository import ReviewRepository
from src.application.ports.out.user_repository import UserRepository
from src.domain.exceptions.book_exceptions import BookNotFound
from src.domain.exceptions.review_exception import PermissionDeniedError, ReviewNotFound
from src.domain.exceptions.user_exceptions import UserNotFound

# --- Dominio ---
from src.domain.review.review import DomainReview
from src.domain.review.value_objects.rating_value import RatingVO
from src.domain.review.value_objects.review_text import ReviewTextVO


class ReviewApplicationService:
    def __init__(
        self,
        review_repository: ReviewRepository,
        book_repository: BookRepository,
        user_repository: UserRepository,
        # book_app_service: BookApplicationService # Alternativa: inyectar el servicio de libros
    ):
        self._review_repository = review_repository
        self._book_repository = book_repository
        self._user_repository = user_repository
        # self._book_app_service = book_app_service

    async def add_review_to_book(
        self,
        book_google_id: str,
        user_id: uuid.UUID,
        rating_input: int,
        review_text_input: str,
    ) -> DomainReview:
        internal_book = await self._book_repository.get_book_by_google_id(
            book_google_id
        )
        if not internal_book:
            raise BookNotFound(
                f'Book with Google ID {book_google_id} must be registered locally (e.g., favorited) before adding a review.'
            )  # TODO: Implement save_book_from_google_if_not_exists

        user = await self._user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFound(f'User with ID {user_id} not found.')

        existing_review = await self._review_repository.get_review_by_user_and_book_id(
            user_id=user_id, book_id=internal_book.id
        )
        if existing_review:
            raise ValueError(
                f"User {user.username} has already reviewed book '{internal_book.title}'."
            )

        try:
            rating_vo = RatingVO(rating_input)
            review_text_vo = ReviewTextVO(review_text_input)
        except ValueError as e:
            raise ValueError(f'Invalid review data: {str(e)}')

        current_time = datetime.now(timezone.utc)
        domain_review = DomainReview(
            id=uuid.uuid4(),
            rating=rating_vo,
            review_text=review_text_vo,
            book_id=internal_book.id,
            user_id=user_id,
            created_at=current_time,
            updated_at=current_time,
        )

        saved_review = await self._review_repository.save_review(domain_review)

        return saved_review

    async def update_user_review(
        self,
        review_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        new_text_input: Optional[str] = None,
        new_rating_input: Optional[int] = None,
    ) -> DomainReview:
        review_to_update = await self._review_repository.get_review_by_id(review_id)
        if not review_to_update:
            raise ReviewNotFound(f'Review with ID {review_id} not found.')

        if review_to_update.user_id != requesting_user_id:
            raise PermissionDeniedError('User not authorized to update this review.')

        review_to_update.update_review(
            new_text=new_text_input, new_rating=new_rating_input
        )

        return await self._review_repository.save_review(review_to_update)

    async def delete_user_review(
        self, review_id: uuid.UUID, requesting_user_id: uuid.UUID
    ) -> None:
        review_to_delete = await self._review_repository.get_review_by_id(review_id)
        if not review_to_delete:
            raise ReviewNotFound()  # TODO: Check this later

        if review_to_delete.user_id != requesting_user_id:
            raise PermissionDeniedError('User not authorized to delete this review.')

        return await self._review_repository.delete_review(review_id)

    async def get_reviews_for_book_by_google_id(
        self, book_google_id: str, limit: int = 10, offset: int = 0
    ) -> List[DomainReview]:
        internal_book = await self._book_repository.get_book_by_google_id(
            book_google_id
        )
        if not internal_book:
            return []
        return await self._review_repository.get_reviews_by_book_id(
            internal_book.id, limit, offset
        )

    async def get_reviews_by_user(
        self, user_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> List[DomainReview]:
        # user = await self._user_repository.get_by_id(user_id)
        # if not user:
        #     raise UserNotFoundDomainError(f"User with ID {user_id} not found.")
        return await self._review_repository.get_reviews_by_user_id(
            user_id, limit, offset
        )
