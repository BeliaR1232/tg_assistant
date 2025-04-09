from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    token: str


class DatabaseSettings(BaseModel):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        return "postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}".format_map(
            self.model_dump()
        )


class Settings(BaseSettings):
    bot: BotSettings
    database: DatabaseSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
