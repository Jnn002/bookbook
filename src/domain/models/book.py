import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional

from src.domain.models.review import DomainReview
from src.domain.models.tags import DomainTag


@dataclass
class DomainBook:
    id: uuid.UUID
    title: str
    authors: list[str]
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime
    user_id_owner: Optional[uuid.UUID] = None
    google_book_id: Optional[str] = None
    cover_image_url: Optional[str] = None
    reviews: list[DomainReview] = field(default_factory=list)
    tags: list[DomainTag] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError('Title cannot be empty')
        # TODO: Check if empty list is allowed
        if not self.authors or not all(
            author and author.strip() for author in self.authors
        ):
            raise ValueError('Authors cannot be empty')
        if not self.publisher or not self.publisher.strip():
            raise ValueError('Publisher cannot be empty')
        if self.published_date > date.today():
            raise ValueError('Published date cannot be in the future')
        if self.page_count <= 0:
            raise ValueError('Page count must be greater than 0')
        if not self.language or not self.language.strip():
            raise ValueError('Language cannot be empty')
        if self.created_at > datetime.now(timezone.utc):
            raise ValueError('Created at cannot be in the future')
        if self.updated_at < self.created_at:
            raise ValueError('Updated at must be greater than or equal to created at')
        # TODO: Evaluate later rules for google_book_id and cover_image_url

    def add_review(self, review: DomainReview) -> None:
        """Add a review to the book"""
        if review not in self.reviews:
            self.reviews.append(review)
            self.updated_at = datetime.now(timezone.utc)

    def add_tag(self, tag_data: DomainTag) -> None:
        """Add tag data to the book"""
        if tag_data not in self.tags:
            self.tags.append(tag_data)
            self.updated_at = datetime.now(timezone.utc)

    def is_externally_sourced(self) -> bool:
        """Check if the book is externally sourced"""
        return self.google_book_id is not None
