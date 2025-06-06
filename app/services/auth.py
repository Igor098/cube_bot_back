import uuid
from datetime import datetime, timezone, timedelta

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from fastapi.responses import Response
from jose import jwt, ExpiredSignatureError, JWTError

from app.constants.enums import TokenType
from app.core import settings
from app.crud.user import UserDAO, UserSessionDAO
from app.models.user import User
from app.schemas.user import UserSessionUpdateFilterModel, UserSessionUpdateModel
from app.utils.exceptions import TokenNoFound, TokenExpiredException, NoJwtException, UserNotFoundException, \
    ForbiddenException, InvalidTokenFormatException, SessionNotValidException
from app.utils.security import create_refresh_token, create_access_token, set_tokens_as_cookies, create_session


async def _get_token_from_request(request: Request, token_type: TokenType) -> str:
    # Пытаемся получить токен из кук
    token_name = token_type.value
    logger.info(f"Token name: {token_name}")
    token = request.cookies.get(token_name)
    if token:
        return token
    # Если нет в куках, пытаемся из заголовков (X-Access-Token / X-Refresh-Token)
    header_name = "X-" + "".join(w.capitalize() for w in token_name.split("_"))
    token = request.headers.get(header_name)
    if token:
        return token
    raise TokenNoFound


async def get_access_token(
    request: Request,
) -> str:
    return await _get_token_from_request(request, TokenType.ACCESS_TOKEN)


async def get_refresh_token(
    request: Request,
) -> str:
    return await _get_token_from_request(request, TokenType.REFRESH_TOKEN)


async def verify_token_and_session(
    token: str,
    token_type: TokenType,
    session: AsyncSession
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        logger.error(f"payload error")
        raise NoJwtException

    is_valid_payload = validate_jwt_payload(payload, token_type)
    if is_valid_payload:
        telegram_id = payload.get("sub")
        session_id = payload.get("sid")

        user = await UserDAO(session).find_one_or_none_by_telegram_id(int(telegram_id))
        if not user:
            raise UserNotFoundException

        user_session = await UserSessionDAO(session).find_one_or_none_by_id(data_id=session_id)
        if (
                not user_session
                or not user_session.is_active
                or user_session.user_id != user.id
        ):
            raise ForbiddenException

        return user


async def refresh_tokens(
    response: Response,
    request: Request,
    session: AsyncSession,
):
    refresh_token = await get_refresh_token(request=request)
    if not refresh_token:
            raise TokenExpiredException

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise NoJwtException

    is_valid_payload = await validate_jwt_payload(payload=payload, token_type=TokenType.REFRESH_TOKEN)
    if is_valid_payload:
        telegram_id = payload.get("sub")
        session_id = payload.get("sid")

        user_session = await UserSessionDAO(session).find_one_or_none_by_id(session_id)
        exp = user_session.expires_at
        now = datetime.now(timezone.utc)

        exp_ts = exp.timestamp()
        new_ts = now.timestamp()

        if (
            not user_session
            or not user_session.is_active
            or exp_ts < new_ts
            or user_session.user.telegram_id != int(telegram_id)
        ):
            raise SessionNotValidException

        await UserSessionDAO(session).update(
            filters=UserSessionUpdateFilterModel(
                id=session_id,
                is_active=True
            ),
            values=UserSessionUpdateModel(is_active=False),
        )

        new_session_id = str(uuid.uuid4())
        user_agent = request.headers.get("User-Agent")

        await create_session(
            session_id=new_session_id,
            user_agent=user_agent,
            user_id=user_session.user_id,
            session=session
        )

        # Всё прошло — генерим новую пару токенов
        new_access_token = await create_access_token(telegram_id, new_session_id)
        new_refresh_token = await create_refresh_token(telegram_id, new_session_id)

        await set_tokens_as_cookies(response, new_access_token, new_refresh_token)
        response.headers["X-Access-Token"] = new_access_token
        response.headers["X-Refresh-Token"] = new_refresh_token
        response.headers["X-Session-ID"] = new_session_id

        return {"message": "Tokens refreshed successfully"}


async def logout(
    response: Response,
    token: str,
    session: AsyncSession
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise NoJwtException

    is_valid_payload = await validate_jwt_payload(payload, TokenType.ACCESS_TOKEN)

    if is_valid_payload:
        user_session_dao = UserSessionDAO(session=session)
        user_dao = UserDAO(session=session)

        session_id = payload.get("sid")
        telegram_id = payload.get("sub")

        user = await user_dao.find_one_or_none_by_telegram_id(telegram_id=telegram_id)
        user_session = await user_session_dao.find_one_or_none_by_id(data_id=session_id)

        if not user or not user_session or user_session.user_id != user.id:
            raise ForbiddenException

        await user_session_dao.update(
            filters=UserSessionUpdateFilterModel(
                id=session_id,
                is_active=True
            ),
            values=UserSessionUpdateModel(is_active=False),
        )

        if response:
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

        return {"logout": True}


async def validate_jwt_payload(payload: dict, token_type: TokenType) -> bool:
    session_id = payload.get("sid")
    telegram_id = payload.get("sub")
    is_valid_issuer = payload.get("iss") == settings.JWT_ISSUER
    is_valid_audience = payload.get("aud") == settings.JWT_AUDIENCE
    is_valid_type = payload.get("type") == token_type.value
    expire_ts = payload.get("exp")
    issued_at_ts = payload.get("iat")

    now = datetime.now(timezone.utc)

    if (
        not session_id
        or not telegram_id
        or not is_valid_type
        or not is_valid_issuer
        or not is_valid_audience
    ):
        raise InvalidTokenFormatException

    if not expire_ts or datetime.fromtimestamp(expire_ts, tz=timezone.utc) < now:
        raise TokenExpiredException

    if not issued_at_ts:
        raise NoJwtException

    issued_at = datetime.fromtimestamp(issued_at_ts, tz=timezone.utc)

    clock_skew = timedelta(seconds=settings.JWT_CLOCK_SKEW_SECONDS)
    if issued_at - now > clock_skew:
        raise NoJwtException

    return True
