import random
from typing import Tuple

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import WordDAO, CategoryDAO
from app.models import Word
from app.schemas import CategoryModel, WordSchema
from app.services.user import get_all_categories


async def select_random_word(category: str, session: AsyncSession) -> Tuple[Word, str]:
    word_dao = WordDAO(session)
    category_dao = CategoryDAO(session)

    if "Случайно" in category:
        categories_obj = await get_all_categories(session)
        categories = categories_obj.get("categories", [])

        category = random.choice(categories)

    logger.info(f"Категория: {category}")

    category = await category_dao.find_one_or_none(filters=CategoryModel(name=category))

    logger.info(f"Категория из базы: {category}")
    category_id = category.id

    if category_id is None:
        raise HTTPException(status_code=404, detail="Category not found")

    word = await word_dao.get_random_word(category_id)

    logger.info(f"Слово: {word}")

    return word, category.name