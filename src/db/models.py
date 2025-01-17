import uuid
from datetime import date, datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import ForeignKey
from sqlmodel import Column, Field, Relationship, SQLModel


# User model
class User(SQLModel, table=True):
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, default='user'))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))
    reviews: list['Review'] = Relationship(
        back_populates='user', sa_relationship_kwargs={'lazy': 'selectin'}
    )
    books: list['Book'] = Relationship(
        back_populates='user', sa_relationship_kwargs={'lazy': 'selectin'}
    )

    def __repr__(self):
        return f'<User {self.username}>'


class BookTag(SQLModel, table=True):
    book_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey('book.uid'), primary_key=True)
    )
    tag_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey('tag.uid'), primary_key=True)
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))


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
    user: Optional['User'] = Relationship(back_populates='books')
    reviews: list['Review'] = Relationship(
        back_populates='book', sa_relationship_kwargs={'lazy': 'selectin'}
    )
    tags: list['Tag'] = Relationship(
        link_model=BookTag,
        back_populates='books',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    def __repr__(self):
        return f'<Book {self.title}>'


class Tag(SQLModel, table=True):
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: list['Book'] = Relationship(
        link_model=BookTag,
        back_populates='tags',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    def __repr__(self):
        return f'<Tag {self.name}>'


class Review(SQLModel, table=True):
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(ge=1, lt=6)
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key='user.uid')
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key='book.uid')
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates='reviews')
    book: Optional[Book] = Relationship(back_populates='reviews')

    def __repr__(self):
        return f'<Review for book {self.book_uid} by user {self.user_uid}>'
