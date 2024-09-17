from os import getenv


class Config:
    token: str = getenv("DEV_BOT_TOKEN") if getenv("DEV_BOT_TOKEN") is not None else getenv("BOT_TOKEN")
    DB_LOGIN: str = getenv("DB_LOGIN")
    DB_PASSWORD: str = getenv("DB_PASSWORD")
    DB_HOST: str = getenv("DB_HOST")
    DB_PORT: int = int(getenv("DB_PORT"))
    DB_DATABASE: str = getenv("DB_DATABASE")
