from pydantic import BaseModel, PositiveInt, Field, StrictBool, ConfigDict


class UserModel(BaseModel):
    telegram_id: PositiveInt = Field(title="Telegram ID", description="Поле с Telegram ID пользователя", examples=[123456789])
    username: str = Field(title="Имя пользователя", description="Поле с именем пользователя", examples=["Ivan", "Kate"])
    is_admin: StrictBool = Field(title="Пользователь является администратором?", description="Поле для проверки прав администратора")

    model_config = ConfigDict(from_attributes=True)