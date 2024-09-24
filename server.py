import codecs
import enum
import platform
import traceback

from sanic import Sanic, Request, SanicException, html, json
from sqlalchemy import select
from telebot import TeleBot

from config import Config
from database import create_tables, session
from database.models import User, Shop

app = Sanic("MineKatalog")
bot = TeleBot(Config.token)

with codecs.open("exception_page.html", "r", "utf-8") as f:
    exception_page = f.read()


class TokenType(enum.Enum):
    USER = 1
    SHOP = 2


@app.on_request
async def get_user(request: Request):
    token = request.credentials
    if token is None:
        raise SanicException(status_code=401, message="Token is empty!")
    async with session() as s:
        if token.auth_type is None:
            user = (await s.execute(select(User).where(User.token == token.token))).scalar_one_or_none()
            if user is not None:
                request.ctx.user = user
                request.ctx.token_type = TokenType.USER
                return
        elif token.auth_type == "Bearer" and "/shops/" in request.path:
            shop = (await s.execute(select(Shop).where(Shop.api_token == token.token))).scalar_one_or_none()
            if shop is not None and shop.shop_id in request.path:
                request.ctx.user = shop
                request.ctx.token_type = TokenType.SHOP
                return
        raise SanicException(status_code=401, message="Token is invalid!")


@app.before_server_start
async def attach_db(app, loop):
    await create_tables()


@app.exception(Exception)
def handle_exception(request: Request, exception: SanicException):
    if isinstance(exception, SanicException):
        if request.method == "GET" and exception.status_code == 401:
            return html(exception_page.replace("{ERROR_MESSAGE}", exception.message), status=exception.status_code)
        return json({"message": exception.message}, status=exception.status_code)
    error = "\n".join(list(map(lambda x: x[:-1], traceback.format_exception(exception))))
    error_message = f"Произошла ошибка:\n```python\n{error}```"
    if "user" in list(request.ctx.__dict__):
        if request.ctx.token_type.value == TokenType.USER:
            try:
                user = bot.get_chat_member(request.ctx.user.tg_id, request.ctx.user.tg_id)
                error_message = error_message + f"\nИнформация о пользователе:\n```USER_INFO\nID пользователя: {request.ctx.user.id}\nTG ID: {request.ctx.user.tg_id}```\n@{user.user.username}"
            except:
                error_message = error_message + f"\nИнформация о пользователе:\n```USER_INFO\nID пользователя: {request.ctx.user.id}\nTG ID: {request.ctx.user.tg_id}```"
        else:
            try:
                user = bot.get_chat_member(request.ctx.user.owner.tg_id, request.ctx.user.owner.tg_id)
                error_message = error_message + f"\nИнформация о пользователе:\n```USER_INFO\nID пользователя: {request.ctx.user.owner_id}\nTG ID: {request.ctx.user.owner.tg_id}```\nОшибка произошла в магазине:\n```SHOP_INFO\nID магазина: {request.ctx.user.id}\nИмя магазина: {request.ctx.user.shop_name}```\n@{user.user.username}"
            except:
                error_message = error_message + f"\nИнформация о пользователе:\n```USER_INFO\nID пользователя: {request.ctx.user.owner_id}\nTG ID: {request.ctx.user.owner.tg_id}```\nОшибка произошла в магазине:\n```SHOP_INFO\nID магазина: {request.ctx.user.id}\nИмя магазина: {request.ctx.user.shop_name}```"
    bot.send_message(Config.MAIN_CHANNEL, error_message,
                     message_thread_id=Config.ERROR_CHANNEL, parse_mode="MarkdownV2")
    return json({"message": "Internal Server Error"}, status=500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=platform.system() == "Windows")
