import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.exceptions.time_exceptions import (
    FutureCreatedAtError,
    NaiveDateTimeError,
    UpdatedBeforeCreatedError,
)
from src.domain.tag.value_objects.tag_name_vo import TagNameVO


@dataclass
class DomainTag:
    id: uuid.UUID
    name: TagNameVO
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise NaiveDateTimeError('Tag - Datetime must be timezone-aware')
        if self.updated_at.tzinfo is None:
            raise NaiveDateTimeError('Tag - Datetime must be timezone-aware')
        if self.created_at > datetime.now(timezone.utc):
            raise FutureCreatedAtError('Tag - Created at cannot be in the future')
        if self.updated_at < self.created_at:
            raise UpdatedBeforeCreatedError(
                'Tag - Updated_at must be greater than or equal to created_at'
            )

    def update_name(self, new_name_value: str) -> None:
        """
        Updates the name of the tag.

        Args:
            new_name_value: The new string value for the tag name.
        """
        new_name_vo = TagNameVO(new_name_value)
        if self.name.value != new_name_vo.value:
            self.name = new_name_vo
            self.updated_at = datetime.now(timezone.utc)
