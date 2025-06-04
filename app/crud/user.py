from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User, UserSession
from app.models.program import Program

from .base import BaseDAO


class UserDAO(BaseDAO):
    model = User

    async def find_one_or_none_by_telegram_id(self, telegram_id: int) -> User:
        try:
            query = select(self.model).filter_by(telegram_id=telegram_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с Telegram ID {telegram_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с Telegram ID {telegram_id}: {e}")
            raise

    async def find_admin_or_none_by_telegram_id(self, telegram_id: int) -> User:
        try:
            query = select(self.model).filter_by(telegram_id=telegram_id, is_admin=True)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} администратора с Telegram ID {telegram_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с Telegram ID {telegram_id}: {e}")
        raise

class UserSessionDAO(BaseDAO):
    model = UserSession

class ProgramDAO(BaseDAO):
    model = Program
