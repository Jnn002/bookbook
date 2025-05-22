from src.application.ports.out.user_repository import UserRepository
from src.domain.user.value_objects.user_email import UserEmailVO


class UserApplicationService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self._user_repository = user_repository

    async def register_user(
        self,
        username: str,
        email_str: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> None:
        try:
            email_vo = UserEmailVO(email_str)
        except ValueError as e:
            raise ValueError(f'Invalid email format: {e}')

        if await self._user_repository.exists_by_email(email_vo):
            raise ValueError('Email already exists')
        if await self._user_repository.exists_by_username(username):
            raise ValueError('Username already exists')

        # TODO: Call hash_password method to hash the password
