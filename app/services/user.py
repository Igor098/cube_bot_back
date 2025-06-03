from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserDAO
from app.models.user import User


async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession) -> User:
    dao = UserDAO(session)
    result = await dao.find_one_or_none_by_telegram_id(telegram_id=telegram_id)
    return result


async def get_all_words(category: str, session: AsyncSession):
    pass