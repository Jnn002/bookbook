import uuid
from datetime import datetime, timezone

from src.application.ports.out.security_port import PasswordSecurityPort
from src.application.ports.out.user_repository import UserRepository
from src.domain.user.user import DomainUser
from src.domain.user.value_objects.user_email import UserEmailVO
from src.domain.user.value_objects.user_name_field import FieldName


class UserApplicationService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_security_port: PasswordSecurityPort,
    ):
        self._user_repository = user_repository
        self._password_security_port = password_security_port

    async def create_user(
        self,
        username: str,
        email_str: str,
        first_name: FieldName,
        last_name: FieldName,
        password: str,
        is_verified: bool = False,
    ) -> DomainUser:
        try:
            email_vo = UserEmailVO(email_str)
        except ValueError as e:
            raise ValueError(f'Invalid email format: {e}')

        if await self._user_repository.exists_by_email(email_vo):
            raise ValueError('Email already exists')
        if await self._user_repository.exists_by_username(username):
            raise ValueError('Username already exists')

        hashed_password = self._password_security_port.hash_password(password)

        current_time = datetime.now(timezone.utc)

        domain_user = DomainUser(
            id=uuid.uuid4(),
            username=username,
            email=email_vo,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            created_at=current_time,
            updated_at=current_time,
            is_verified=is_verified,
        )

        saved_user = await self._user_repository.save_user(domain_user)
        return saved_user
