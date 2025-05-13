import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional

from src.domain.book.value_objects.isbn_vo import IsbnVO
from src.domain.exceptions.book_exceptions import (
    EmptyAuthors,
    EmptyCoverImageUrl,
    EmptyGoogleBookId,
    EmptyLanguage,
    EmptyPublisher,
    EmptyTitle,
    InvalidPageCount,
    InvalidPublishedDate,
)
from src.domain.exceptions.time_exceptions import (
    FutureCreatedAtError,
    NaiveDateTimeError,
    UpdatedBeforeCreatedError,
)
from src.domain.review.review import DomainReview
from src.domain.tag.tags import DomainTag


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
    cover_image_url: str
    google_book_id: str
    isbn: Optional[IsbnVO] = None
    reviews: list[DomainReview] = field(default_factory=list)
    tags: list[DomainTag] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise EmptyTitle('Book - Title cannot be empty')
        if not self.authors or not all(
            author and author.strip() for author in self.authors
        ):
            raise EmptyAuthors('Book - Authors cannot be empty')
        if not self.publisher or not self.publisher.strip():
            raise EmptyPublisher('Book - Publisher cannot be empty')
        if self.published_date > date.today():
            raise InvalidPublishedDate('Book - Published date cannot be in the future')
        if self.page_count <= 0:
            raise InvalidPageCount('Book - Page count must be positive')
        if not self.language or not self.language.strip():
            raise EmptyLanguage('Book - Language cannot be empty')
        if self.created_at.tzinfo is None:
            raise NaiveDateTimeError('Book - Datetime must be timezone-aware')
        if self.updated_at.tzinfo is None:
            raise NaiveDateTimeError('Book - Datetime must be timezone-aware')
        if self.created_at > datetime.now(timezone.utc):
            raise FutureCreatedAtError('Book - Created at cannot be in the future')
        if self.updated_at < self.created_at:
            raise UpdatedBeforeCreatedError(
                'Book - Updated at must be greater than or equal to created at'
            )
        if not self.google_book_id or not self.google_book_id.strip():
            raise EmptyGoogleBookId('Book - Google Book ID cannot be empty')
        if not self.cover_image_url or not self.cover_image_url.strip():
            raise EmptyCoverImageUrl('Book - Cover image URL cannot be empty')

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
