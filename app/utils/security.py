import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from fastapi.responses import Response

from app.models.user import User, UserSession
from app.core import settings
from app.crud.user import UserSessionDAO
from app.schemas.user import UserSessionCreateModel, UserSessionFilterModel, UserSessionModel


def create_jwt_token(telegram_id: int, session_id: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(tz=timezone.utc) + expires_delta
    payload = {
        "sub": str(telegram_id),
        "sid": session_id,
        "exp": int(expire.timestamp()),
        "type": token_type
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def create_access_token(telegram_id: int, session_id: str) -> str:
    return create_jwt_token(
        telegram_id,
        session_id=session_id,
        expires_delta=timedelta(days=settings.ACCESS_EXPIRE_MINUTES),
        token_type="access"
    )


async def create_refresh_token(telegram_id: int, session_id: str) -> str:
    return create_jwt_token(
        telegram_id,
        session_id=session_id,
        expires_delta=timedelta(days=settings.REFRESH_EXPIRE_DAYS),
        token_type="refresh"
    )


async def issue_tokens(user: User, request: Request, response: Response, session: AsyncSession):
    user_agent = request.headers.get("User-Agent")
    existing_session = await UserSessionDAO(session=session).find_one_or_none(
        filters=UserSessionFilterModel(
            user_id=user.id,
            user_agent=user_agent,
            is_active=True
        )
    )
    if existing_session:
        session_id = existing_session.id
    else:
        session_id = str(uuid.uuid4())
        await create_session(
            session_id,
            user_agent=user_agent,
            user_id=user.id,
            session=session
        )

    access_token = await create_access_token(telegram_id=user.telegram_id, session_id=session_id)
    refresh_token = await create_refresh_token(telegram_id=user.telegram_id, session_id=session_id)

    await set_tokens_as_cookies(response, access_token, refresh_token)
    response.headers["X-Access-Token"] = access_token
    response.headers["X-Refresh-Token"] = refresh_token
    response.headers["X-Session-ID"] = session_id

    return {"completed": True}


async def set_tokens_as_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, secure=True, samesite="lax"
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=True, samesite="lax"
    )

async def create_session(session_id: str, user_agent: str, user_id: int, session: AsyncSession) -> str:
    now = datetime.now(tz=timezone.utc)

    user_session = UserSessionCreateModel(
        id=session_id,
        user_agent=user_agent,
        user_id=user_id,
        created_at=now,
        expires_at=now + timedelta(days=settings.REFRESH_EXPIRE_DAYS),
        is_active=True
    )
    return await UserSessionDAO(session=session).add(user_session)