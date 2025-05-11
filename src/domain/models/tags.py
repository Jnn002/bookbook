import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DomainTag:
    id: uuid.UUID
    name: str
    created_at: datetime

    def __post_init__(self) -> None:
        self.name = self.name.strip().lower()
        if not self.name:
            raise ValueError('Name cannot be empty')
        if self.created_at.tzinfo is None:
            raise ValueError('created_at must be a timezone-aware datetime object')
        if self.created_at > datetime.now(timezone.utc):
            raise ValueError('Created at cannot be in the future')
        if len(self.name) > 20:
            raise ValueError('Name cannot be longer than 20 characters')

    # TODO: check later if we will need to implement a method to update the tag name
