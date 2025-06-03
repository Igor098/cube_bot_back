from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends.dao_dep import get_session_with_commit
from app.services.user import get_user_by_telegram_id

from app.schemas.user import UserModel

router = APIRouter(prefix="/v1/user", tags=["User"])


@router.get("/me", response_model=UserModel)
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session_with_commit)) -> UserModel:
    user = await get_user_by_telegram_id(telegram_id=telegram_id, session=session)
    if not user:
        raise HTTPException(status_code=404)

    return UserModel.model_validate(user)

