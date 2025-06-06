from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import TokenType
from app.depends.dao_dep import get_session_without_commit
from app.models.user import User
from app.services.auth import get_access_token, verify_token_and_session, get_refresh_token
from app.utils.exceptions import SessionNotValidException


async def get_current_user(
    token: str = Depends(get_access_token),
    session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    user = await verify_token_and_session(token=token, token_type=TokenType.ACCESS_TOKEN, session=session)
    if not user:
        raise SessionNotValidException
    return user


async def check_access_token(
    token: str = Depends(get_access_token),
    session: AsyncSession = Depends(get_session_without_commit)
) -> bool:
    user = await verify_token_and_session(token=token, token_type=TokenType.ACCESS_TOKEN, session=session)
    if not user:
        return False
    return True


async def check_refresh_token(
    token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_session_without_commit)
) -> bool:
    user = await verify_token_and_session(token=token, token_type=TokenType.REFRESH_TOKEN, session=session)
    if not user:
        return False
    return True