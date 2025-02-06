from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.service import BookService
from src.errors import BookNotFound

from ..db.main import get_session
from .schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel

role_checker = Depends(RoleChecker(['admin', 'user']))


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get('/', response_model=list[Book], dependencies=[role_checker])
async def get_all_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_detail=Depends(access_token_bearer),
):
    """Get all books
    Args: None
    Returns: list[Book]: A list of all books"""
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    '/{book_uid}', response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_book(
    book_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_detail: dict = Depends(access_token_bearer),
):
    """Get a book by its uid
    Args: book_uid (str): The book uid
    Returns: BookDetailModel: The book details"""
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFound()


@book_router.get(
    '/user/{user_uid}', response_model=list[Book], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_detail=Depends(access_token_bearer),
):
    """Get all books submitted by a user
    Args: user_uid (str): The user uid
    Returns: list[Book]: A list of books submitted by the current user
    """
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_detail: dict = Depends(access_token_bearer),
):
    """Create a new book
    Args: book_data (BookCreateModel): The book data to be created
    Returns: Book: The created book

    """
    user_uid = token_detail['user']['user_uid']
    new_book = await book_service.create_book(book_data, session, user_uid)
    return new_book


@book_router.patch('/{book_uid}', response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_detail: dict = Depends(access_token_bearer),
):
    """Update a book
    Args: book_uid (str): The book uid to be updated
    REturns: Book: The updated book
    """
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book is None:
        raise BookNotFound()
    else:
        return updated_book


@book_router.delete(
    '/{book_uid}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker],
)
async def delete_book(
    book_uid: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_detail: dict = Depends(access_token_bearer),
):
    """Delete a book
    Args: book_uid (str): The book uid to be deleted
    Returns: dict: An empty dictionary
    """
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete is None:
        raise BookNotFound()
    else:
        return {}
