import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainTag:
    id: uuid.UUID
    name: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError('Name must be a string')
        if not isinstance(self.created_at, datetime):
            raise TypeError('Created at must be a datetime object')
        if not self.name or not self.name.strip():
            raise ValueError('Name cannot be empty')
        if self.created_at > datetime.now():
            raise ValueError('Created at cannot be in the future')
