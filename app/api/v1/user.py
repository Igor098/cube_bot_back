from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserDAO
from app.depends.auth_dep import get_current_user
from app.depends.dao_dep import get_session_with_commit
from app.models.user import User
from app.schemas.user import UserModel, UserCreateModel, UserUpdateModel, UserDeleteModel, UserUpdateBodyModel
from app.services.user import create_user, update_user, delete_user
from app.utils.exceptions import UserAlreadyExistsException, IncorrectDataException

router = APIRouter(prefix="/v1/user", tags=["User"])

@router.post("/register", response_model=UserModel)
async def create_user_listener(
        user: UserCreateModel,
        session: AsyncSession = Depends(get_session_with_commit),
) -> UserModel:
    dao = UserDAO(session)
    is_available = dao.find_admin_or_none_by_telegram_id(user.telegram_id)
    if is_available:
        raise UserAlreadyExistsException
    new_user = await create_user(user=user, session=session)

    if not new_user:
        raise IncorrectDataException

    return UserModel.model_validate(new_user)


@router.patch("/update", response_model=UserUpdateModel)
async def update_user_listener(
        body: UserUpdateBodyModel,
        user_data: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session_with_commit),

) -> UserUpdateModel:

    updated_user = await update_user(
        telegram_id=user_data.telegram_id,
        user=body,
        session=session
    )

    return updated_user


@router.delete("/delete")
async def delete_user_listener(
        user_data: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session_with_commit),
) -> UserDeleteModel:
    deleted_user = await delete_user(telegram_id=user_data.telegram_id, session=session)

    return deleted_user