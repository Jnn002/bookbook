import uuid
from datetime import datetime

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Book

from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        """Get all books from database
        Args:
            session (AsyncSession): Database session
        Returns:
            List[Book]: List of all books
        """
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        """Get all books of a user
        Args:
            user_uid (str): User uid
            session (AsyncSession): Database session
        Returns:
            List[Book]: List of all books of a user"""
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )

        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        """Get a book by uid
        Args:
            book_uid (str): Book uid
            session (AsyncSession): Database session
        Returns:
            Book: Book object if found, None otherwise"""
        statement = select(Book).where(Book.uid == book_uid)

        result = await session.exec(statement)
        book = result.first()

        return book if book is not None else None

    async def create_book(
        self, book_data: BookCreateModel, session: AsyncSession, user_uid: uuid.UUID
    ):
        """Create a new book
        Args:
            book_data (BookCreateModel): Book data
            session (AsyncSession): Database session
            user_uid (uuid.UUID): User uid

        Returns:
            Book: Created book object"""
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)

        new_book.published_date = datetime.strptime(
            book_data_dict['published_date'], '%Y-%m-%d'
        )

        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()

        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        """Update a book
        Args:
            book_uid (str): Book uid
            update_data (BookUpdateModel): Updated book data
            session (AsyncSession): Database session
        Returns:
            Book: Updated book object if found, None otherwise"""
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()

            for key, value in update_data_dict.items():
                setattr(book_to_update, key, value)

            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        """Delete a book
        Args:
            book_uid (str): Book uid
            session (AsyncSession): Database session
        Returns:
            Dict: Empty dictionary if book is deleted"""
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()

            return {}
        else:
            return None
