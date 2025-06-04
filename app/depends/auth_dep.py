from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends.dao_dep import get_session_without_commit
from app.models.user import User
from app.services.auth import get_access_token, verify_token_and_session, get_refresh_token


async def get_current_user(
    token: str = Depends(get_access_token),
    session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    return await verify_token_and_session(token, token_type="access", session=session)


async def check_refresh_token(
    token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_session_without_commit)
) -> User:
    return await verify_token_and_session(token, token_type="refresh", session=session)