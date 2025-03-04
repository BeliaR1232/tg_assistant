from sqlalchemy import select

from src.database import Category
from src.repository.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Репозиторий для работы с категориями."""

    def __init__(self, session):
        super().__init__(session, Category)

    async def get_category_by_alias(self, category_alias: str) -> Category:
        """Получает категорию по псевдониму."""
        stmt = select(Category).where(Category.aliases.has_key(category_alias))
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            stmt = select(Category).where(Category.aliases.has_key("прочее"))
            result = await self.session.execute(stmt)
            category = result.scalar_one()

        return category
