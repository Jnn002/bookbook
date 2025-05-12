import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.models.exceptions.tags_exception import EmptyName, NameTooLong
from src.domain.models.exceptions.time_exceptions import (
    FutureCreatedAtError,
    NaiveDateTimeError,
)


@dataclass
class DomainTag:
    id: uuid.UUID
    name: str
    created_at: datetime

    def __post_init__(self) -> None:
        self.name = self.name.strip().lower()
        if not self.name:
            raise EmptyName('Tag name cannot be empty')
        if self.created_at.tzinfo is None:
            raise NaiveDateTimeError('Tag - Datetime must be timezone-aware')
        if self.created_at > datetime.now(timezone.utc):
            raise FutureCreatedAtError('Tag - Created at cannot be in the future')
        if len(self.name) > 20:
            raise NameTooLong('Tag name must be 20 characters or less')

    # TODO: check later if we will need to implement a method to update the tag name
