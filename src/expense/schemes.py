from datetime import datetime

from pydantic import BaseModel, Field


class CategoryScheme(BaseModel):
    id: int
    codename: str
    name: str
    is_base_expense: bool
    expenses: list["ExpenseScheme"] = Field(default_factory=list)


class ExpenseScheme(BaseModel):
    id: int
    amount: float
    category_name: str
    user_id: int
    category_id: int


class ExpenseCreateScheme(BaseModel):
    amount: float
    category_name: str
    description: str | None


class AssetsScheme(BaseModel):
    codename: str
    amount: int
    name: str
    user_id: int


class UserScheme(BaseModel):
    id: int
    telegram_id: int
    chat_id: int
    name: str
    lastname: str | None
    is_active: bool
    expenses: list["ExpenseScheme"] = Field(default_factory=list)
    assets: list["AssetsScheme"] = Field(default_factory=list)


class ExpenseTopScheme(BaseModel):
    id: int
    amount: float
    category_name: str
    created_at: datetime
    description: str | None


class ExpenseStatisticScheme(BaseModel):
    amount: float
    category_name: str
