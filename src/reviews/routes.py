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
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )

    return new_review


@review_router.get('/', dependencies=[user_role_checker])
async def get_all_reviews(session: Annotated[AsyncSession, Depends(get_session)]):
    reviews = await review_service.get_all_reviews(session)
    return reviews


@review_router.get('/{review_uid}', response_model=ReviewModel)
async def get_review(
    review_uid: str, session: Annotated[AsyncSession, Depends(get_session)]
):
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
    await review_service.delete_review_from_book(
        review_uid, current_user.email, session
    )

    return {'message': 'Review deleted'}


# TODO: Add update_review route
