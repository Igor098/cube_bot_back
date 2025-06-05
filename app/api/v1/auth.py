from fastapi.responses import Response
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request

from app.crud.user import UserDAO
from app.depends.auth_dep import get_current_user
from app.depends.dao_dep import get_session_with_commit, get_session_without_commit
from app.models.user import User
from app.services.auth import refresh_tokens, logout, get_access_token

from app.schemas.user import UserModel
from app.utils.exceptions import UserNotFoundException, ServerErrorException
from app.utils.security import issue_tokens

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


@router.get("/me", response_model=UserModel)
async def get_user_listener(
        user_data: User = Depends(get_current_user)
) -> UserModel:
    return UserModel.model_validate(user_data)


@router.post("/login", response_model=UserModel)
async def login_listener(
        telegram_id: int,
        request: Request,
        response: Response,
        session: AsyncSession = Depends(get_session_with_commit)
) -> UserModel:
    dao = UserDAO(session)
    user = await dao.find_one_or_none_by_telegram_id(
        telegram_id=telegram_id,
    )

    if not user:
        raise UserNotFoundException

    is_authenticated = await issue_tokens(user=user, request=request, response=response, session=session)

    if not is_authenticated:
        raise ServerErrorException

    return UserModel.model_validate(user)


@router.get("/refresh")
async def refresh_tokens_listener(
        response: Response,
        request: Request,
        session: AsyncSession = Depends(get_session_with_commit)
):
    return await refresh_tokens(response=response, request=request, session=session)


@router.post("/logout")
async def logout_listener(
        response: Response,
        token: str = Depends(get_access_token),
        session: AsyncSession = Depends(get_session_with_commit),
):
    return await logout(response=response, token=token, session=session)
