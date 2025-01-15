from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

from .dependencies import AccessTokenBearer, RefreshTokenBearer
from .schemas import UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, verify_password

auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post(
    '/signup', response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_account(user_data: UserCreateModel, session=Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User with this email already exists',
        )
    else:
        new_user = await user_service.create_user(user_data, session)
        return new_user


@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session=Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={'email': user.email, 'user_uid': str(user.uid)}
            )

            refresh_token = create_access_token(
                user_data={'email': user.email, 'user_uid': str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    'message': 'Login succesful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {'email': user.email},
                }
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password'
    )


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc) > datetime.now(
        timezone.utc
    ):
        new_access_token = create_access_token(
            user_data=token_details['user'], refresh=False
        )
        return JSONResponse(content={'access_token': new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail='Sorry, invalid token'
    )


@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={'message': 'You have logged out'}, status_code=status.HTTP_200_OK
    )
