import uuid
from datetime import date, datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

from src.auth import models


class Book(SQLModel, table=True):
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key='user.uid')
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))
    user: Optional['models.User'] = Relationship(back_populates='books')

    def __repr__(self):
        return f'<Book {self.title}>'
