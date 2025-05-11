import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DomainReview:
    # TODO: Check book_uid and user_uid mandatory
    id: uuid.UUID
    rating: int
    review_text: Optional[str]
    book_uid: Optional[uuid.UUID]
    user_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not (1 <= self.rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
        if self.review_text is not None and not isinstance(self.review_text, str):
            raise TypeError('Review text must be a string')
        # TODO: Check if empty list is allowed
        if self.book_uid is None:
            raise ValueError('Book UID cannot be None')
        if self.user_uid is None:
            raise ValueError('User UID cannot be None')
        if self.created_at > datetime.now(timezone.utc):
            raise ValueError('Created at cannot be in the future')
        if self.updated_at > datetime.now(timezone.utc):
            raise ValueError('Updated at cannot be in the future')
        if self.updated_at < self.created_at:
            raise ValueError(
                'Updated at least should be greater than or equal to created at'
            )

        if not isinstance(self.review_text, str):
            raise TypeError('Review text must be a string')
        if not isinstance(self.created_at, datetime):
            raise TypeError('Created at must be a datetime object')
        if not isinstance(self.updated_at, datetime):
            raise TypeError('Updated at must be a datetime object')

    def update_review(
        self, new_text: Optional[str] = None, new_rating: Optional[int] = None
    ) -> None:
        """Update the review text and update the updated_at timestamp"""
        updated = False

        if new_text is not None:
            if self.review_text != new_text:
                self.review_text = new_text
                updated = True

        if new_rating is not None:
            if not (1 <= new_rating <= 5):
                raise ValueError('Rating must be between 1 and 5')
            self.rating = new_rating
            updated = True

        if updated:
            self.updated_at = datetime.now(timezone.utc)
