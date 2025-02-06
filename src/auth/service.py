from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User

from .schemas import UserCreateModel
from .utils import generate_password_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        """get user by email from database
        Args:
            email (str): email of the user
            session (AsyncSession): database session
        Returns:
            User: user object
        """
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)
        user = result.first()

        return user

    async def user_exists(self, email: str, session: AsyncSession):
        """check if user exists in database
        Args:
            email (str): email of the user
            session (AsyncSession): database session
        Returns:
            bool: True if user exists else False
        """
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        """create new user in database
        Args:
            user_data (UserCreateModel): user data
            session (AsyncSession): database session
        Returns:
            User: user object
        """
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict['password'])
        new_user.role = 'user'

        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        """update user data in database
        Args:
            user (User): user object
            user_data (dict): user data
            session (AsyncSession): database session
        Returns:
            User: updated user object
        """
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return user
