from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User

from .schemas import UserCreateModel
from .utils import generate_password_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        # SELECT * FROM user WHERE email = email
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()
        # devolver el usuario
        return user

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        # TODO: Hash the password before saving
        new_user.password_hash = generate_password_hash(user_data_dict['password'])
        # TODO: Implement a role system
        new_user.role = 'user'

        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return user
