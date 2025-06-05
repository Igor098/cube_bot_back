import uuid
from datetime import datetime, timezone, time

from fastapi import Depends, Cookie
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from fastapi.responses import Response
from jose import jwt, ExpiredSignatureError, JWTError

from app.core import settings
from app.crud.user import UserDAO, UserSessionDAO
from app.depends.dao_dep import get_session_without_commit, get_session_with_commit
from app.models.user import User, UserSession
from app.schemas.user import UserSessionCreateModel, UserSessionUpdateFilterModel, UserSessionModel
from app.utils.exceptions import TokenNoFound, TokenExpiredException, NoJwtException, UserNotFoundException, \
    ForbiddenException, InvalidTokenFormatException, SessionNotValidException
from app.utils.security import create_refresh_token, create_access_token, set_tokens_as_cookies, create_session


def _get_token_from_request(request: Request, token_name: str) -> str:
    # Пытаемся получить токен из кук
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
    return _get_token_from_request(request, "access_token")


async def get_refresh_token(
    request: Request,
) -> str:
    return _get_token_from_request(request, "refresh_token")


async def verify_token_and_session(
    token: str,
    token_type: str,
    session: AsyncSession
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        logger.error(f"payload error: payload: {payload}")
        raise NoJwtException

    # Проверяем тип токена
    if payload.get("type") != token_type:
        logger.error(f"payload type error: {payload}, type: {token_type}")
        raise NoJwtException

    # Проверяем срок жизни
    expire_ts = payload.get("exp")
    if not expire_ts or datetime.fromtimestamp(expire_ts, tz=timezone.utc) < datetime.now(timezone.utc):
        raise TokenExpiredException

    telegram_id = payload.get("sub")
    session_id = payload.get("sid")
    if not telegram_id or not session_id:
        logger.error(f"tg or session error: tg: {telegram_id}, session: {session_id}")
        raise NoJwtException

    # Проверяем пользователя
    user = await UserDAO(session).find_one_or_none_by_telegram_id(int(telegram_id))
    if not user:
        raise UserNotFoundException

    # Проверяем сессию
    user_session = await UserSessionDAO(session).find_one_or_none_by_id(data_id=session_id)
    if not user_session or not user_session.is_active or user_session.user_id != user.id:
        raise ForbiddenException

    return user


async def refresh_tokens(
    response: Response,
    request: Request,
    session: AsyncSession,
):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
            raise TokenExpiredException

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception:
        raise NoJwtException

    telegram_id = payload.get("sub")
    session_id = payload.get("sid")

    if not telegram_id or not session_id:
        raise InvalidTokenFormatException

    user_session = await UserSessionDAO(session).find_one_or_none_by_id(session_id)
    logger.info(f"user >>> {user_session.user}")
    logger.info(UserSessionCreateModel.model_validate(user_session))
    exp = user_session.expires_at
    now = datetime.now(timezone.utc)

    exp_ts = exp.timestamp()
    new_ts = now.timestamp()

    logger.debug(f"exp = {type(exp)}, now = {type(now)}")
    logger.debug(f"exp_ts = {exp_ts}, new_ts = {new_ts}")

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
        values=UserSessionModel(is_active=False),
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
    logger.info(f"logout >>> {token}")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    session_id = payload.get("sid")

    user_session = await UserSessionDAO(session).find_one_or_none_by_id(data_id=session_id)
    if user_session:
        await UserSessionDAO(session=session).update(
            filters=UserSessionUpdateFilterModel(
                id=session_id,
                is_active=True
            ),
            values=UserSessionModel(is_active=False),
        )

    if response:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

    return {"logout": True}