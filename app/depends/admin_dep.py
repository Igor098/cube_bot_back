from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.crud.user import UserDAO
from app.depends.dao_dep import get_session_with_commit


async def check_admin_privileges(request: Request, session: AsyncSession = Depends(get_session_with_commit)):
    admin_telegram_id = request.query_params.get("admin_telegram_id", None)
    if not admin_telegram_id:
        raise HTTPException(400, detail="Отсутствует поле Telegram ID")

    if admin_telegram_id.isdigit():
        admin_telegram_id = int(admin_telegram_id)
    else:
        raise HTTPException(400, "Некорректный Telegram ID администратора")

    dao = UserDAO(session)
    is_admin = await dao.find_admin_or_none_by_telegram_id(telegram_id=admin_telegram_id)
    if not is_admin:
        raise HTTPException(401, "Пользователь с таким Telegram ID не является администратором")
