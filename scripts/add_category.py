import asyncio
import logging

from sqlalchemy.exc import IntegrityError

from src.database import db_helper
from src.database.models import Category

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__file__)

categoryes = [
    {
        "codename": "products",
        "name": "продукты",
        "aliases": ["еда", "окей", "рынок", "овощи", "мясо", "фрукты"],
        "is_base_expense": True,
    },
    {
        "codename": "medicine",
        "name": "здоровье",
        "aliases": ["здоровье", "медицина", "аптека", "таблетки", "доктор", "анализы", "лекарства"],
        "is_base_expense": True,
    },
    {
        "codename": "connection",
        "name": "связь",
        "aliases": ["интернет", "мобильная связь", "связь", "мегафон", "домру"],
        "is_base_expense": True,
    },
    {
        "codename": "animals",
        "name": "животные",
        "aliases": [
            "собака",
            "кошка",
            "ветеринарный врач",
            "ветлечебница",
            "Аксель",
            "вкусняшки",
            "кинолог",
        ],
        "is_base_expense": True,
    },
    {
        "codename": "fuel",
        "name": "топливо",
        "aliases": ["бензин", "лукойл", "заправка"],
        "is_base_expense": True,
    },
    {
        "codename": "car",
        "name": "машина",
        "aliases": ["сервис", "то", "страховка", "мойка"],
        "is_base_expense": False,
    },
    {
        "codename": "entertaiment",
        "name": "развлечение",
        "aliases": ["кино", "каток", "картинг", "парк", "игры", "гости"],
        "is_base_expense": False,
    },
    {
        "codename": "cafe",
        "name": "кафе",
        "aliases": [
            "ресторан",
            "рест",
            "мак",
            "макдоналдс",
            "макдак",
            "kfc",
            "кфс",
            "пицца",
            "суши",
            "гирос",
            "шаурма",
            "бургеры",
        ],
        "is_base_expense": False,
    },
    {
        "codename": "trip",
        "name": "путешествие",
        "aliases": ["поездка"],
        "is_base_expense": False,
    },
    {
        "codename": "gift",
        "name": "подарки",
        "aliases": [],
        "is_base_expense": False,
    },
    {
        "codename": "credit",
        "name": "кредит",
        "aliases": [],
        "is_base_expense": True,
    },
    {
        "codename": "appliance",
        "name": "техника",
        "aliases": ["днс"],
        "is_base_expense": False,
    },
    {
        "codename": "other",
        "name": "прочее",
        "aliases": [],
        "is_base_expense": False,
    },
    {
        "codename": "books",
        "name": "книги",
        "aliases": [],
        "is_base_expense": False,
    },
    {
        "codename": "taxi",
        "name": "такси",
        "aliases": [],
        "is_base_expense": False,
    },
    {
        "codename": "cloth",
        "name": "одежда",
        "aliases": [],
        "is_base_expense": False,
    },
    {
        "codename": "sport",
        "name": "спорт",
        "aliases": ["айкидо", "спортзал", "зал"],
        "is_base_expense": False,
    },
    {
        "codename": "home",
        "name": "дом",
        "aliases": ["леруа", "ремонт"],
        "is_base_expense": False,
    },
]


async def add_category():
    session = db_helper.session_factory()
    for cat in categoryes:
        cat["aliases"].append(cat["name"])
        cat["aliases"] = list(map(lambda x: x.lower(), cat["aliases"]))
        category = Category(**cat)
        session.add(category)
        try:
            await session.commit()
            logger.info(f"Добавленна категория {cat['name']}.")
        except IntegrityError:
            logger.info(f"Категория {cat['name']} уже существует.")
            await session.rollback()
    await session.close()


if __name__ == "__main__":
    asyncio.run(add_category())
