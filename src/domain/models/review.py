import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DomainReview:
    id: uuid.UUID
    rating: int
    review_text: str
    book_uid: uuid.UUID
    user_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    def _validate_review_text(self, text_to_validate: str) -> None:
        """Validate that the review text is not empty and does not exceed 500 characters."""
        if not text_to_validate.strip():
            raise ValueError('Review text cannot be empty')
        if len(text_to_validate) > 500:
            raise ValueError('Review text cannot exceed 500 characters')

    def _validate_rating(self, rating: int) -> None:
        """Validate that the rating is between 1 and 5."""
        if not (1 <= rating <= 5):
            raise ValueError('Rating must be between 1 and 5')

    def __post_init__(self):
        self._validate_rating(self.rating)
        self._validate_review_text(self.review_text)
        if self.created_at.tzinfo is None:
            raise ValueError('created_at must be a timezone-aware datetime object')
        if self.updated_at.tzinfo is None:
            raise ValueError('updated_at must be a timezone-aware datetime object')
        if self.created_at > datetime.now(timezone.utc):
            raise ValueError('Created at cannot be in the future')
        if self.updated_at < self.created_at:
            raise ValueError('Updated at should be greater than or equal to created at')

    def update_review(
        self, new_text: Optional[str] = None, new_rating: Optional[int] = None
    ) -> None:
        """Update the review text and update the updated_at timestamp."""
        original_text = self.review_text
        original_rating = self.rating

        if new_text is not None:
            self._validate_review_text(new_text)
            self.review_text = new_text

        if new_rating is not None:
            self._validate_rating(new_rating)
            self.rating = new_rating

        if self.review_text != original_text or self.rating != original_rating:
            self.updated_at = datetime.now(timezone.utc)
