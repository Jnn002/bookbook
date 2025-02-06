"""Authentication and Authorization dependencies module.

This module provides token bearer authentication for the FastAPI application.
It handles JWT token validation, decoding, and blacklist checking.

Example:
    from auth.dependencies import TokenBearer

    @router.get("/protected")
    async def protected_route(token_data: dict = Depends(TokenBearer())):
        return {"message": "Access granted"}
"""

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.db.redis import token_in_blocklist
from src.errors import (
    AccessTokenRequired,
    AccountNotVerified,
    InsufficientPermission,
    InvalidCredentials,
    InvalidToken,
    RefreshTokenRequired,
)

from .service import UserService
from .utils import decode_token

user_service = UserService()


class TokenBearer(HTTPBearer):
    """
    Custom token bearer authentication class.

    Extends FastAPI's HTTPBearer to provide JWT validation and blacklist checking.

    Attributes:
        auto_error (bool): Whether to auto-raise HTTP 403 on validation failure

    Raises:
        InvalidCredentials: When no valid credentials are provided
        InvalidToken: When token is invalid or in blacklist
    """

    def __init__(self, auto_error=True):
        """Initialize TokenBearer.

        Args:
            auto_error (bool, optional): Enable auto error responses. Defaults to True.
        """
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        """Validate and process the bearer token from request.

        Args:
            request (Request): FastAPI request object

        Returns:
            dict: Decoded token data containing user information

        Raises:
            InvalidCredentials: When no credentials provided
            InvalidToken: When token is invalid or blacklisted

        TokenBearer subclasses must implement the verify_token_data method.
        """
        creds = await super().__call__(request)

        if creds is None:
            raise InvalidCredentials()

        token = creds.credentials
        token_data = decode_token(token)

        if not token_data:
            raise InvalidToken()

        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError('Subclasses must implement this method')


class AccessTokenBearer(TokenBearer):
    """Bearer token validator for access tokens.

    Validates that the provided token is an access token, not a refresh token.

    Raises:
        AccessTokenRequired: When a refresh token is provided instead of access token

    Example:
        @router.get("/protected")
        async def protected_route(token=Depends(AccessTokenBearer())):
            return {"message": "Valid access token"}
    """

    def verify_token_data(self, token_data: dict) -> None:
        """Verify token is an access token.

        Args:
            token_data (dict): Decoded JWT token data

        Raises:
            AccessTokenRequired: When token is a refresh token
        """
        if token_data and token_data['refresh']:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    """Bearer token validator for refresh tokens.

    Validates that the provided token is a refresh token, not an access token.

    Raises:
        RefreshTokenRequired: When an access token is provided instead of refresh token

    Example:
        @router.post("/refresh")
        async def refresh_token(token=Depends(RefreshTokenBearer())):
            return {"message": "Valid refresh token"}
    """

    def verify_token_data(self, token_data: dict) -> None:
        """Verify token is a refresh token.

        Args:
            token_data (dict): Decoded JWT token data

        Raises:
            RefreshTokenRequired: When token is an access token
        """
        if token_data and not token_data['refresh']:
            raise RefreshTokenRequired()


async def get_current_userd(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    """Get current authenticated user from token.

    Dependency that extracts user details from the provided access token
    and retrieves the full user object from database.

    Args:
        token_details (dict): Decoded JWT token data
        session (AsyncSession): Database session

    Returns:
        User: Current authenticated user object

    Example:
        @router.get("/me")
        async def get_my_profile(user: User = Depends(get_current_userd)):
            return user
    """
    user_email = token_details['user']['email']

    user = await user_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    # TODO: complete Rolechecker implementation
    """Role-based access control checker.

    Validates that the current user has one of the allowed roles.

    Attributes:
        allow_roles (list[str]): List of roles that are allowed access

    Raises:
        AccountNotVerified: When user's email is not verified
        InsufficientPermission: When user's role is not in allowed roles

    Example:
        admin_required = RoleChecker(["admin"])

        @router.delete("/users/{user_id}")
        async def delete_user(user_id: str, _=Depends(admin_required)):
            return {"message": "User deleted"}
    """

    def __init__(self, allow_roles: list[str]):
        """Initialize role checker with allowed roles.

        Args:
            allow_roles (list[str]): List of roles that are allowed access
        """
        self.allow_roles = allow_roles

    def __call__(self, current_user: User = Depends(get_current_userd)):
        """Check if current user has required role.

        Args:
            current_user (User): Current authenticated user

        Returns:
            bool: True if user has required role

        Raises:
            AccountNotVerified: When user's email is not verified
            InsufficientPermission: When user's role is not allowed
        """
        if not current_user.is_verified:
            raise AccountNotVerified()

        if current_user.role in self.allow_roles:
            return True

        raise InsufficientPermission()
