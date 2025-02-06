import logging
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from src.config import Config

password_context = CryptContext(schemes=['bcrypt'])
serializer = URLSafeTimedSerializer(secret_key=Config.JWT_SECRET, salt='email-config')

ACCESS_TOKEN_EXPIRY = 2700


def generate_password_hash(password: str) -> str:
    """generate password hash using bcrypt"""
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    """compare and verify password with bcrypt hash"""
    return password_context.verify(password, hash)


def create_access_token(
    user_data: dict,
    expiry: timedelta | None = None,
    refresh: bool = False,
):
    """create jwt access token

    definifies the payload for the jwt token and encodes it using the jwt library"""
    if expiry:
        expire_token_time = datetime.now(timezone.utc) + expiry
    else:
        expire_token_time = datetime.now(timezone.utc) + timedelta(
            seconds=ACCESS_TOKEN_EXPIRY
        )
    payload = {
        'user': user_data,
        'exp': expire_token_time,
        'jti': str(uuid.uuid4()),
        'refresh': refresh,
    }

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str):
    """decodes jwt token and returns the payload"""
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data

    except jwt.ExpiredSignatureError as e:
        logging.exception(f'Token expired: {e}')
        return None
    except jwt.InvalidTokenError as e:
        logging.exception(f'Invalid token: {e}')
        return None
    except jwt.PyJWTError as e:
        logging.exception(f'Error decoding token: {e}')
        return None


def create_url_safe_token(data: dict):
    """create a url safe token using itsdangerous library
    this token can be used in urls and is url safe"""
    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    """decode url safe token and return the payload
    this token is created using itsdangerous library"""
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(f'Error decoding token: {e}')
        return None
