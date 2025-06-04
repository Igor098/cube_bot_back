import uuid
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, PositiveInt, Field, StrictBool, ConfigDict


class UserModel(BaseModel):
    telegram_id: PositiveInt = Field(title="Telegram ID", description="Поле с Telegram ID пользователя", examples=[123456789])
    username: str = Field(title="Имя пользователя", description="Поле с именем пользователя", examples=["Ivan", "Kate"])
    is_admin: StrictBool = Field(title="Пользователь является администратором?", description="Поле для проверки прав администратора")

    model_config = ConfigDict(from_attributes=True)


class UserCreateModel(BaseModel):
    telegram_id: PositiveInt = Field(title="Telegram ID", description="Поле с Telegram ID пользователя",
                                     examples=[123456789])
    username: str = Field(title="Имя пользователя", description="Поле с именем пользователя", examples=["Ivan", "Kate"])


class UserUpdateBodyModel(BaseModel):
    username: Optional[str] = Field(title="Имя пользователя", description="Поле с именем пользователя",
                                    examples=["Ivan", "Kate"])
    is_admin: Optional[StrictBool] = Field(title="Пользователь является администратором?",
                                           description="Поле для проверки прав администратора")


class UserUpdateModel(UserModel):
    is_updated:Optional[StrictBool] = Field(title="Пользователь обновлен?",
                                           description="Поле для проверки обновления пользователя")


class UserUpdateFilterModel(BaseModel):
    telegram_id: PositiveInt = Field(title="Telegram ID", description="Поле с Telegram ID пользователя",
                                     examples=[123456789])


class UserDeleteModel(UserModel):
    is_deleted: StrictBool = Field(title="Пользователь удален?", description="Поле для проверки удаления пользователя")


class UserSessionModel(BaseModel):
    id: str = Field()
    user_id: int = Field()
    user_agent: str = Field()
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)