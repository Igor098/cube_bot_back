from enum import Enum

class Age(Enum):
    CHILD = "5 - 7 лет"
    PRE_TEEN = "8 - 12 лет"
    TEENAGER = "13 - 18 лет"


class TokenType(Enum):
    ACCESS_TOKEN = "access-token"
    REFRESH_TOKEN = "refresh-token"
