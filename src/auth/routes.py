from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_userd,
)
from .schemas import UserBooksModel, UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, verify_password

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])

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
    # consulta a la base de datos

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        # verificar la contraseña que se ingreso con la que esta en la base de datos
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            # crear el token de acceso
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role,
                },
            )
            # crear el token de refresh
            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role,
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )
            # retornar el token de acceso y el token de refresh
            return JSONResponse(
                content={
                    'message': 'Login succesful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {'email': user.email, 'user_uid': str(user.uid)},
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


# we are getting our current user and their own related books that they have submitted
@auth_router.get('/me', response_model=UserBooksModel)
async def get_current_user(user=Depends(get_current_userd)):
    return user


@auth_router.get('/logout')
async def revoke_token(
    token_details: dict = Depends(AccessTokenBearer()), _: bool = Depends(role_checker)
):
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={'message': 'You have logged out'}, status_code=status.HTTP_200_OK
    )
