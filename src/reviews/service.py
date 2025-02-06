from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.errors import BookNotFound, ReviewNotFoundOrUserIsNotOwner, UserNotFound

from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        """Add a review to a book
        Args:
            user_email (str): The user email
            book_uid (str): The book uid
            review_data (ReviewCreateModel): The review data
            session (AsyncSession): The database session
        Returns: The new review
        Raises: errors.BookNotFound, errors.UserNotFound"""
        try:
            book = await book_service.get_book(book_uid, session)
            user = await user_service.get_user_by_email(user_email, session)

            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)

            if not book:
                raise BookNotFound()

            if not user:
                raise UserNotFound()

            new_review.book = book
            new_review.user = user

            session.add(new_review)
            await session.commit()

            return new_review

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    async def get_all_reviews(self, session: AsyncSession):
        """Get all reviews from the database
        Args:
            session (AsyncSession): The database session
        Returns: All reviews
        """
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)
        return result.all()

    async def get_review(self, review_uid: str, session: AsyncSession):
        """Get a review by its uid from the database
        Args: review_uid (str): The review uid
        session (AsyncSession): The database session

        Returns: The specific review"""
        statement = select(Review).where(Review.uid == review_uid)

        result = await session.exec(statement)
        return result.first()

    async def delete_review_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        """Delete a review by its uid
        Args:
            review_uid (str): The review uid
            user_email (str): The user email
            session (AsyncSession): The database session
        Raises: errors.ReviewNotFoundOrUserIsNotOwner"""
        user = await user_service.get_user_by_email(user_email, session)

        review = await self.get_review(review_uid, session)

        if not review or (review.user != user):
            raise ReviewNotFoundOrUserIsNotOwner()

        await session.delete(review)
        await session.commit()
