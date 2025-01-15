from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from src.db.redis import token_in_blocklist

from .utils import decode_token


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    # Request) -> HTTPAuthorizationCredentials | None
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        creds = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid authorization credentials',
            )

        token = creds.credentials
        token_data = decode_token(token)

        # TODO: Debug this validation to check for redundant token validation
        """ if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid or expired token(1)',
            ) """

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid or expired token(2)',
            )

        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Token has been revoked or has expired',
            )

        self.verify_token_data(token_data)

        return token_data

    # TODO: debug this method, until that this method will be suspended
    """ def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return True if token_data is not None else False """

    def verify_token_data(self, token_data):
        raise NotImplementedError('Subclasses must implement this method')


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Access Token Required'
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Refresh Token Required'
            )
