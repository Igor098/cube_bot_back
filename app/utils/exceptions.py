
from fastapi import status, HTTPException

# Пользователь уже существует
UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь уже существует'
)

# Пользователь не найден
UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Пользователь не найден'
)

# Отсутствует идентификатор пользователя
UserIdNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Отсутствует идентификатор пользователя'
)

# Неверная почта или пароль
IncorrectDataException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Неверные данные'
)

# Токен истек
TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Токен истек'
)

# Некорректный формат токена
InvalidTokenFormatException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Некорректный формат токена'
)


# Токен отсутствует в заголовке
TokenNoFound = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Токен отсутствует в заголовке'
)

# Невалидный JWT токен
NoJwtException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Токен не валидный'
)

# Не найден ID пользователя
NoUserIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Не найден ID пользователя'
)

# Недостаточно прав
ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Недостаточно прав'
)

TokenInvalidFormatException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неверный формат токена. Ожидается 'Bearer <токен>'"
)

SessionNotValidException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Сессия неактивна или истек срок ее действия"
)

ServerErrorException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Внутренняя ошибка сервера"
)
