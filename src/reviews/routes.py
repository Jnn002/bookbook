from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_userd
from src.db.main import get_session
from src.db.models import User
from src.errors import ReviewNotFound

from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()

admin_role_checker = Depends(RoleChecker(['admin']))
user_role_checker = Depends(RoleChecker(['admin', 'user']))


@review_router.post('/books/{book_uid}', dependencies=[user_role_checker])
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: Annotated[User, Depends(get_current_userd)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Add a review to a book
    Args:
        book_uid (str): The book uid
        review_data (ReviewCreateModel): The review data
        current_user (User): The current user
        session (AsyncSession): The database session
    Service: review_service.add_review_to_book
    Returns: The new review"""
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )

    return new_review


@review_router.get('/', dependencies=[user_role_checker])
async def get_all_reviews(session: Annotated[AsyncSession, Depends(get_session)]):
    """Get all reviews
    Args:
        session (AsyncSession): The database session
    Service: review_service.get_all_reviews
    Returns: All reviews"""
    reviews = await review_service.get_all_reviews(session)
    return reviews


@review_router.get('/{review_uid}', response_model=ReviewModel)
async def get_review(
    review_uid: str, session: Annotated[AsyncSession, Depends(get_session)]
):
    """Get a review by its uid
    Args: review_uid (str): The review uid
    Returns: The specific review
    Service: review_service.get_review
    Raises: ReviewNotFound: If the review is not found"""
    review = await review_service.get_review(review_uid, session)

    if review:
        return review
    else:
        raise ReviewNotFound()


@review_router.delete('/delete/{review_uid}', dependencies=[user_role_checker])
async def delete_review(
    review_uid: str,
    current_user: Annotated[User, Depends(get_current_userd)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Delete a review by its uid
    Args: review_uid (str): The review uid, current_user (User): The current user
    Service: review_service.delete_review_from_book
    Returns: A message confirming the deletion
    """
    await review_service.delete_review_from_book(
        review_uid, current_user.email, session
    )

    return {'message': 'Review deleted'}


# TODO: Add update_review route
