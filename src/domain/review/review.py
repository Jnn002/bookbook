import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from src.domain.exceptions.time_exceptions import (
    FutureCreatedAtError,
    NaiveDateTimeError,
    UpdatedBeforeCreatedError,
)
from src.domain.review.value_objects.rating_value import RatingVO
from src.domain.review.value_objects.review_text import ReviewTextVO


@dataclass
class DomainReview:
    id: uuid.UUID
    rating: RatingVO
    review_text: ReviewTextVO
    book_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Post-initialization validation for the review."""
        if self.created_at.tzinfo is None:
            raise NaiveDateTimeError('Create Review - Datetime must be timezone-aware')
        if self.updated_at.tzinfo is None:
            raise NaiveDateTimeError('Update Review - Datetime must be timezone-aware')
        if self.created_at > datetime.now(timezone.utc):
            raise FutureCreatedAtError('Review - Created at cannot be in the future')
        if self.updated_at < self.created_at:
            raise UpdatedBeforeCreatedError(
                'Review - Updated at must be greater than or equal to created at'
            )

    def update_review(
        self, new_text: Optional[str] = None, new_rating: Optional[int] = None
    ) -> None:
        """
        Update the review text and/or rating, and update the updated_at timestamp.

        Args:
            new_text: The new text for the review. If None, text is not changed.
            new_rating: The new rating for the review. If None, rating is not changed.

        Raises:
            EmptyReview: If new_text is empty or whitespace.
            LengthExceeded: If new_text exceeds the maximum allowed length.
            InvalidRating: If new_rating is not between 1 and 5.
        """
        has_changed = False

        if new_text is not None and self.review_text.value != new_text:
            self.review_text = ReviewTextVO(new_text)
            has_changed = True

        if new_rating is not None and self.rating.value != new_rating:
            self.rating = RatingVO(new_rating)
            has_changed = True

        if has_changed:
            self.updated_at = datetime.now(timezone.utc)
