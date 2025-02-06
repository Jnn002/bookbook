import uuid
from datetime import datetime

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.db.models import Tag
from src.errors import BookNotFound, TagAlreadyExists, TagNotFound

from .schemas import TagAddModel, TagCreateModel

book_service = BookService()


""" server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong'
) """


class TagService:
    async def get_all_tags(self, session: AsyncSession):
        """Get all tags from the database
        Args:
            session (AsyncSession): The database session
        Returns:
            List[Tag]: List of tags
        """
        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.exec(statement)

        return result.all()

    async def add_tags_to_book(
        self, book_uid: str, tag_data: TagAddModel, session: AsyncSession
    ):
        """Add tags to a book
        If tag not found, create a new tag

        Args:
            book_uid (str): The book uid
            tag_data (TagAddModel): The tag data
            session (AsyncSession): The database session
        Returns:
            Book: The book with the tags added
        Raises:
            errors.BookNotFound: If the book is not found"""
        book = await book_service.get_book(book_uid=book_uid, session=session)

        if not book:
            raise BookNotFound()

        for tag_item in tag_data.tags:
            result = await session.exec(select(Tag).where(Tag.name == tag_item.name))

            tag = result.one_or_none()
            if not tag:
                tag = Tag(
                    name=tag_item.name, uid=uuid.uuid4(), created_at=datetime.now()
                )

            book.tags.append(tag)
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        """Get a tag by its uid from the database
        Args:
            tag_uid (str): The tag uid
            session (AsyncSession): The database session
        Returns:
            Tag: The tag
        """
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)

        return result.first()

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        """Add a new tag to the database
        Args:
            tag_data (TagCreateModel): The tag data
            session (AsyncSession): The database session
        Returns:
            Tag: The newly created tag
        Raises:
            errors.TagAlreadyExists: If the tag already exists"""
        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.exec(statement)
        tag = result.first()

        if tag:
            raise TagAlreadyExists()

        new_tag_dict = tag_data.model_dump()
        new_tag = Tag(**new_tag_dict)
        new_tag.name = tag_data.name

        session.add(new_tag)
        await session.commit()

        return new_tag

    async def update_tag(
        self, tag_uid, tag_update_data: TagCreateModel, session: AsyncSession
    ):
        """Update a tag in the database by its uid
        Args:
            tag_uid (str): The tag uid
            tag_update_data (TagCreateModel): The tag data
            session (AsyncSession): The database session
        Returns:
            Tag: The updated tag
        Raises:
            errors.TagNotFound: If the tag is not found"""
        tag = await self.get_tag_by_uid(tag_uid, session)
        if not tag:
            raise TagNotFound()

        update_data_dict = tag_update_data.model_dump()

        for k, v in update_data_dict.items():
            setattr(tag, k, v)

            await session.commit()
            await session.refresh(tag)

        return tag

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        """Delete a tag from the database by its uid
        Args:
            tag_uid (str): The tag uid
            session (AsyncSession): The database session
        Raises:
            errors.TagNotFound: If the tag is not found"""
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFound()

        await session.delete(tag)
        await session.commit()
