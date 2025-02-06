from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker
from src.books.schemas import Book
from src.db.main import get_session

from .schemas import TagAddModel, TagCreateModel, TagModel
from .service import TagService

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(['user', 'admin']))


@tags_router.get('/', response_model=list[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: Annotated[AsyncSession, Depends(get_session)]):
    """Get all tags
    Args:
        None
    Returns:
        List of all tags
    """
    tags = await tag_service.get_all_tags(session)

    return tags


@tags_router.post(
    '/',
    response_model=TagModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[user_role_checker],
)
async def add_tag(
    tag_data: TagCreateModel, session: Annotated[AsyncSession, Depends(get_session)]
):
    """Add a new tag
    Args:
        tag_data: TagCreateModel - tag data to be added
    Returns:
        TagModel - tag added
    """
    tag_added = await tag_service.add_tag(tag_data, session)

    return tag_added


@tags_router.patch(
    '/{tag_uid}', response_model=TagModel, dependencies=[user_role_checker]
)
async def update_tag(
    tag_uid: str,
    tag_update_data: TagCreateModel,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Updae a tag by tag_uid
    Args:
        tag_uid: str - tag uid to be updated
        tag_update_data: TagCreateModel - tag data to be updated
    Returns:
        TagModel - updated tag
    """
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)

    return updated_tag


@tags_router.delete('/{tag_uid}', dependencies=[user_role_checker])
async def delete_tag(
    tag_uid: str, session: Annotated[AsyncSession, Depends(get_session)]
):
    """Delete a tag by tag_uid
    Args:
        tag_uid: str - tag uid to be deleted
    Returns:
        dict - message -> Tag deleted successfully
    """
    await tag_service.delete_tag(tag_uid, session)
    return {'message': 'Tag deleted successfully'}


@tags_router.post(
    '/book/{book_uid}/tags', response_model=Book, dependencies=[user_role_checker]
)
async def add_tags_to_book(
    book_uid: str,
    tag_data: TagAddModel,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Add tags to a book
    Args:
        book_uid: str - book uid to which tags are to be added
        tag_data: TagAddModel - tag data to be added to book
    Returns:
        Book - book with tags added
    """
    book_with_tag = await tag_service.add_tags_to_book(
        book_uid=book_uid, tag_data=tag_data, session=session
    )

    return book_with_tag
