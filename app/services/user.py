from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserDAO
from app.models.user import User
from app.schemas.user import UserCreateModel, UserUpdateBodyModel, UserUpdateFilterModel,UserDeleteModel, \
    UserUpdateModel


async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession) -> User:
    dao = UserDAO(session)
    result = await dao.find_one_or_none_by_telegram_id(telegram_id=telegram_id)
    return result


async def create_user(user: UserCreateModel, session: AsyncSession) -> User:
    dao = UserDAO(session)
    result = await dao.add(user)
    return result


async def update_user(telegram_id: int, user: UserUpdateBodyModel, session: AsyncSession) -> UserUpdateModel:
    dao = UserDAO(session)
    result = await dao.update(
        filters=UserUpdateFilterModel(telegram_id=telegram_id),
        values=user
    )
    if not result:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")

    user = UserUpdateModel.model_validate(result)
    user.is_updated = True

    return user


async def delete_user(telegram_id: int, session: AsyncSession) -> UserDeleteModel:
    dao = UserDAO(session)
    result = await dao.delete(filters=UserUpdateFilterModel(telegram_id=telegram_id))

    if not result:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user = UserDeleteModel.model_validate(result)
    user.is_deleted = True

    return user
