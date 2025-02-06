from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_tasks import send_email_tsk
from src.config import Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.errors import (
    InvalidCredentials,
    InvalidToken,
    PasswordsDoNotMatch,
    UserAlreadyExists,
    UserNotFound,
)
from src.utils.template_manager import template_manager

from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_userd,
)
from .schemas import (
    EmailModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
)
from .service import UserService
from .utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    generate_password_hash,
    verify_password,
)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])


@auth_router.post('/send_mail')
async def send_mail(emails: EmailModel):
    email_list = emails.addresses
    html = '<h1>Mail test</h1>'
    subject = 'Welcome to BookWorld'

    send_email_tsk.delay(email_list, subject, html)  # type: ignore

    return {'message': 'Email sent'}


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel,
    background_tasks: BackgroundTasks,
    session=Depends(get_session),
):
    """Create a new user account

    Args:
        user_data: UserCreateModel: User data to create a new account
        background_tasks: BackgroundTasks: FastAPI background task
        session: AsyncSession: Database session

    Returns:
        dict: Response message and user data

    Raises:
        UserAlreadyExists: If user with the email already exists

    Services:
        - Check if user with the email already exists
        - Create a new user account
        - Send verification email to the user
            email with verification link to verify the account
            based on jinja2 template

    """
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()
    else:
        new_user = await user_service.create_user(user_data, session)
        token = create_url_safe_token({'email': email})
        link = f'http://{Config.DOMAIN}/api/0.2.1/auth/verify/{token}'

        emails = [email]
        subject = 'Verify Your Email Address'

        username = user_data.username

        html = template_manager.render_template(
            'verify_account.html', verification_link=link, user_name=username
        )

        send_email_tsk.delay(emails, subject, html)  # type: ignore

        return {
            'message': 'Account Created! Please check your email to verify your account',
            'user': new_user,
        }


@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session=Depends(get_session)):
    """Login user
    Args:
        login_data: UserLoginModel: User login data
        session: AsyncSession: Database session
    Returns:
        dict: Response message and access token

    Raises:
        InvalidCredentials: If user credentials are invalid

    Services:
        - Get user by email
        - Verify user password
        - Create access token
        - Create refresh token"""
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role,
                },
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role,
                },
                refresh=True,
                expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRY),
                # check functionality
            )

            return JSONResponse(
                content={
                    'message': 'Login succesful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {'email': user.email, 'user_uid': str(user.uid)},
                }
            )
    raise InvalidCredentials()


@auth_router.get('/refresh_token')
async def get_new_access_token(
    token_details: Annotated[dict, Depends(RefreshTokenBearer())],
):
    """Get new access token
    Args:
        token_details: dict: Token details
    Returns:
        dict: New access token
    Raises:
        InvalidToken: If token is invalid"""
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc) > datetime.now(
        timezone.utc
    ):
        new_access_token = create_access_token(
            user_data=token_details['user'], refresh=False
        )
        return JSONResponse(content={'access_token': new_access_token})

    raise InvalidToken()


@auth_router.get('/me', response_model=UserBooksModel)
async def get_current_user(user=Depends(get_current_userd)):
    """Get current user
    Args:
        user: dict: Current user data
    Returns:
        dict: Current user data"""
    return user


@auth_router.get('/logout')
async def revoke_token(
    token_details: Annotated[dict, Depends(AccessTokenBearer())],
    _: bool = Depends(role_checker),
):
    """Revoke token
    Args:
        token_details: dict: Token details
    Returns:
        dict: Response message
    Raises:
        InvalidToken: If token is invalid
    Services:
        - Add token to blocklist

    will be used to revoke the token when the user logs out
    """
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={'message': 'You have logged out'}, status_code=status.HTTP_200_OK
    )


@auth_router.get('/verify/{token}')
async def verify_user_account(
    token: str, session: Annotated[AsyncSession, Depends(get_session)]
):
    """Verify user account
    Args:
        token: str: Verification token
        session: AsyncSession: Database session
    Returns:
        dict: Response message
    Raises:
        InvalidToken: If token is invalid
        UserNotFound: If user is not found
    Services:
        - Decode token
        - Get user by email
        - Update user -> update account to verified"""
    token_data = decode_url_safe_token(token)

    if token_data is None:
        raise InvalidToken()
    user_email = token_data.get('email')
    user_email = token_data['email']

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {'is_verified': True}, session)

        return JSONResponse(
            content={'message': 'Account verified'}, status_code=status.HTTP_200_OK
        )

    return JSONResponse(
        content={'message': 'Something went wrong, please try later'},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post('/password-reset-request')
async def password_reset_request(email_data: PasswordResetRequestModel):
    """Password reset request
    Args:
        email_data: PasswordResetRequestModel: Email data
    Returns:
        dict: Response message
    Services:
        - Create token
        - Send email with token
        - Render email template

    will be used to send an email to the user with a link to reset their password
    this endpoint will be used when the user forgets their password and implements a
    celery task to send the email"""
    email = email_data.email

    token = create_url_safe_token({'email': email})
    link = f'http://{Config.DOMAIN}/api/0.2.1/auth/password-reset-confirm/{token}'

    html_message = template_manager.render_template(
        'reset_password.html', reset_link=link
    )

    subject = 'Reset Your Password'

    send_email_tsk.delay([email], subject, html_message)  # type: ignore

    return JSONResponse(
        content={
            'message': 'Please check your email for instructions to reset your password',
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Reset account password
    Args:
        token: str: Reset password token
        passwords: PasswordResetConfirmModel: New password data
        session: AsyncSession: Database session
    Returns:
        dict: Response message
    Raises:
        PasswordsDoNotMatch: If passwords do not match
        InvalidToken: If token is invalid
        UserNotFound: If user is not found
    Services:
        - Decode token
        - Get user by email
        - Update user -> update password"""
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise PasswordsDoNotMatch()

    token_data = decode_url_safe_token(token)

    if token_data is None:
        raise InvalidToken()
    user_email = token_data['email']

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        passwd_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {'password_hash': passwd_hash}, session)

        return JSONResponse(
            content={'message': 'Password reset successfully'},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={'message': 'Something went wrong, please try again'},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
