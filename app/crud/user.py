from app.models.user import User
from app.models.program import Program

from .base import BaseDAO


class UserDAO(BaseDAO):
    model = User

class ProgramDAO(BaseDAO):
    model = Program
