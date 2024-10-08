import base64
import codecs
import datetime
import enum
import platform
import traceback
import urllib.parse
from json import loads
from random import randbytes

import aiohttp
from sanic import Sanic, Request, SanicException, html, json
from sqlalchemy import select, update
from telebot import TeleBot
from telebot.async_telebot import AsyncTeleBot
from telebot.util import validate_web_app_data

from config import Config
from database import create_tables, session
from database.models import User, Shop

app = Sanic("MineKatalog")
bot = TeleBot(Config.token)

avatars_cache = {}

with codecs.open("exception_page.html", "r", "utf-8") as f:
    exception_page = f.read()


class TokenType(enum.Enum):
    USER = 1
    SHOP = 2


def get_color(chat_id: int) -> str:
    return {
        0: "linear-gradient(#FF845E, #D45246)",
        1: "linear-gradient(#FEBB5B, #F68136)",
        2: "linear-gradient(#B694F9, #6C61DF)",
        3: "linear-gradient(#9AD164, #46BA43)",
        4: "linear-gradient(#53edd6, #28c9b7)",
        5: "linear-gradient(#5CAFFA, #408ACF)",
        6: "linear-gradient(#FF8AAC, #D95574)",
    }[abs(chat_id) % 7]


async def get_user_photo(user: int):
    temp_bot = AsyncTeleBot(Config.token)
    if user in avatars_cache and datetime.datetime.now().timestamp() < avatars_cache[user]["time"]:
        return avatars_cache[user]["avatar"]
    async with aiohttp.ClientSession() as http_session:
        try:
            photos = (await temp_bot.get_user_profile_photos(user)).photos
            photo_id = photos[len(photos) - 1][0].file_id
            photo_url = await temp_bot.get_file_url(photo_id)
            async with http_session.get(photo_url) as res:
                photo_data = (False, await res.read())
        except IndexError:
            photo_data = (True, get_color(user))
    avatars_cache[user] = {"time": (datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp(),
                           "avatar": photo_data}
    return photo_data


@app.on_request
async def get_user(request: Request):
    if request.path == "/auth":
        return
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


def generate_token(user_id: int):
    return base64.b64encode(str(f"User {user_id}").encode() + randbytes(50)).decode()


def shop_to_json(shop: Shop, all_info: bool = False):
    info = {
        "id": shop.id,
        "shop_id": shop.shop_id,
        "name": shop.shop_name,
        "mc_nickname": shop.mc_nickname,
        "position": shop.shop_position,
        "rating": shop.rating,
        "work_time": shop.work_time,
    }
    if all_info:
        info["subscribe_paid"] = shop.subscribe_paid
        info["promos"] = shop.available_promos
        info["working"] = shop.working
    return info


async def user_to_json(user: User):
    avatar = await get_user_photo(user.tg_id)
    return {
        "id": user.id,
        "tg_id": user.tg_id,
        "language": user.language,
        "balance": user.balance,
        "cart": user.cart,
        "linked_cards": user.linked_cards,
        "shops": [shop_to_json(shop, True) for shop in user.shops],
        "orders": [{"id": order.id, "order_id": order.order_id, "status": order.status, "items": order.ordered_items}
                   for order in user.orders],
        "default_avatar": avatar[0],
        "avatar": 'data:image/png;base64, ' + base64.b64encode(avatar[1]).decode() if avatar[0] is False else avatar[1]
    }


def parse_raw_init_data(raw_init_data: str) -> dict:
    data = raw_init_data.split("&")
    parsed = {}
    for item in data:
        spl = item.split("=")
        spl[1] = urllib.parse.unquote(spl[1])
        if spl[1].startswith("{") and spl[1].endswith("}"):
            spl[1] = loads(spl[1])
        parsed[spl[0]] = spl[1]
    return parsed


@app.post("/auth")
async def get_token(request: Request):
    info = request.json
    if "raw_init_data" not in info or "init_data" not in info:
        raise SanicException(status_code=400, message="Invalid raw_init_data")
    parsed = parse_raw_init_data(info["raw_init_data"])
    for key, value in info["init_data"].items():
        if value != parsed[key]:
            raise SanicException(status_code=400, message="Invalid raw_init_data")
    if datetime.datetime.now() - datetime.datetime.fromtimestamp(
            int(info["init_data"]["auth_date"])) > datetime.timedelta(hours=1):
        raise SanicException(status_code=400, message="Invalid raw_init_data")
    valid = validate_web_app_data(Config.token, info["raw_init_data"])
    if not valid:
        raise SanicException(status_code=400, message="Invalid raw_init_data")
    async with session() as s:
        user = (await s.execute(select(User).where(User.tg_id == parsed["user"]["id"]))).scalar_one_or_none()
        token = generate_token(parsed["user"]["id"])
        expired_at = datetime.datetime.now() + datetime.timedelta(days=1)
        if user is None:
            user = User(tg_id=parsed["user"]["id"], token=token, expired_at=expired_at)
            s.add(user)
        else:
            await s.execute(
                update(User).where(User.id == user.id).values({User.token: token, User.expired_at: expired_at}))
        await s.flush()
        await s.refresh(user)
        user = await user_to_json(user)
        user["type"] = "user"
        await s.commit()
        return json(user, headers={"Authorization": token})


@app.get("/me")
async def get_user_info(request: Request):
    info = {"type": "shop" if request.ctx.token_type == TokenType.SHOP else "user"}
    if request.ctx.token_type == TokenType.SHOP:
        info.update(shop_to_json(request.ctx.user, True))
    else:
        info.update(await user_to_json(request.ctx.user))
    return json(info)


@app.before_server_start
async def attach_db(app, loop):
    await create_tables()


def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


@app.exception(Exception)
def handle_exception(request: Request, exception: SanicException):
    if isinstance(exception, SanicException):
        if request.method == "GET" and exception.status_code == 401:
            return html(exception_page.replace("{ERROR_MESSAGE}", exception.message), status=exception.status_code)
        return json({"message": exception.message}, status=exception.status_code)
    exc = traceback.format_exception(exception)
    error = "\n".join(list(map(lambda x: x[:-1].replace("\\", "\\\\"), exc)))
    error_message = f"Произошла ошибка:\n```python\n{error}```"
    if "user" in list(request.ctx.__dict__):
        if request.ctx.token_type == TokenType.USER:
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
    for message in chunkstring(error_message, 4095):
        bot.send_message(Config.MAIN_CHANNEL, message,
                         message_thread_id=Config.ERROR_CHANNEL, parse_mode="MarkdownV2")
    return json({"message": "Internal Server Error"}, status=500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=platform.system() == "Windows", auto_reload=True)
