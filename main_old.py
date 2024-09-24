import asyncio
import logging
import math

import asyncstdlib as a
import telebot
from sqlalchemy import select, or_, update
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from config import Config
from database import create_tables, session
from database.models import User, Server, MCItem, Item, Shop

bot = AsyncTeleBot(Config.token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
users_temp = {}


@bot.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id in users_temp:
        del users_temp[message.from_user.id]
    async with session() as s:
        user_db = (await s.execute(select(User).where(User.tg_id == message.from_user.id))).scalar_one_or_none()
        if user_db is None:
            s.add(User(tg_id=message.from_user.id))
            await s.commit()
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Открыть список серверов", switch_inline_query_current_chat="server_list"))
        await bot.reply_to(message, "Выберите действие", reply_markup=markup)


async def gen_servers_result(servers: list[Server] = None):
    result = []
    if servers is None:
        async with session() as s:
            servers = (await s.execute(select(Server))).scalars().all()
    for server in servers:
        result.append(
            types.InlineQueryResultArticle(server.id, server.server_name,
                                           types.InputTextMessageContent(server.server_name), description=server.domain,
                                           thumbnail_url=server.logo))
    return result


async def get_mc_item(item_id: str | int) -> MCItem:
    async with session() as s:
        if isinstance(item_id, str):
            mc_item = (await s.execute(select(MCItem).where(MCItem.mc_id == item_id))).scalar_one_or_none()
        else:
            mc_item = (await s.execute(select(MCItem).where(MCItem.id == item_id))).scalar_one_or_none()
        return mc_item


async def get_shop(shop_id: int) -> Shop:
    async with session() as s:
        shop = (await s.execute(select(Shop).where(Shop.id == shop_id))).scalar_one_or_none()
        return shop


async def get_item(item_id: int) -> Item:
    async with session() as s:
        item = (await s.execute(select(Item).where(Item.id == item_id))).scalar_one_or_none()
        return item


sell_types = {"piece": {"russian": "от", "english": "from"}, "stack": {"russian": "по", "english": "of"}}
pcs = {"russian": "шт.", "english": "pc."}


async def price_sort(x: Item):
    return x.price


async def rating_sort(x: Item):
    return (await get_shop(x.shop_id)).rating


async def amount_sort(x: Item):
    return x.amount


async def gen_items_result(server: Server, search: str, filter_type: str):
    result = []
    item_name_cache = {}
    sort = price_sort if filter_type == "цена" else rating_sort if filter_type == "рейтинг" else amount_sort if filter_type == "кол-во" else price_sort
    if search == '' or search == 'название предмета':
        items = list(
            await a.sorted(server.items, key=sort, reverse=(filter_type == "рейтинг" or filter_type == "кол-во")))
        result.append(
            types.InlineQueryResultArticle(0, "Найти по фильтрам",
                                           types.InputTextMessageContent(f"Я хочу найти по фильтрам"),
                                           thumbnail_url="https://minekatalog.saddeststoryevertold.ru/images/search.png"))
    else:
        async with session() as s:
            items_names = (await s.execute(select(MCItem).where(
                or_(MCItem.ru_name.ilike(f"%{search}%"), MCItem.en_name.ilike(f"%{search}%"))))).scalars().all()
            items = []
            for item_name in items_names:
                item_name_cache[item_name.mc_id] = item_name
                item = (await s.execute(select(Item).where(Item.item_id == item_name.mc_id,
                                                           Item.server_id == server.id))).scalar_one_or_none()
                if item is not None:
                    items.append(item)
            items = list(
                await a.sorted(items, key=sort, reverse=(filter_type == "рейтинг" or filter_type == "кол-во")))
    filter_type = "price" if filter_type == "цена" else "rating" if filter_type == "рейтинг" else "amount" if filter_type == "кол-во" else "price"
    for item in items:
        item: Item
        if item.item_id in item_name_cache:
            mc_item = item_name_cache[item.item_id]
        else:
            mc_item = await get_mc_item(item.item_id)
        shop = await get_shop(item.shop_id)
        if shop.working and shop.subscribe_paid and not item.hide and item.amount > 0 and item.amount >= item.min_amount:
            curr_item = await get_mc_item(item.currency)
            result.append(
                types.InlineQueryResultArticle(item.id, mc_item.ru_name,
                                               types.InputTextMessageContent(
                                                   f"Я хочу заказать {item.id};{filter_type}"),
                                               description=f"{shop.shop_name} - {item.price} {curr_item.ru_name.lower()}\nПокупка {sell_types[item.sell_type]['russian']} {item.min_amount} {pcs['russian']}",
                                               thumbnail_url=mc_item.image_url))
    return result


async def message_is_server_name(message: types.Message):
    async with session() as s:
        server = (await s.execute(select(Server).where(Server.server_name == message.text))).scalar_one_or_none()
        return server is not None, server


# @bot.callback_query_handler(func=lambda call: call.data == "open_server_list")
# async def open_server_list(call: types.CallbackQuery):
#     await bot.edit_message_text("Выберите сервер", call.message.chat.id, call.message.message_id, reply_markup=)

@bot.inline_handler(lambda query: query.query == "server_list")
async def server_list(query: types.InlineQuery):
    await bot.answer_inline_query(query.id, await gen_servers_result(), cache_time=1)


async def get_server(server_id: int) -> Server | None:
    async with session() as s:
        return (await s.execute(select(Server).where(Server.id == server_id))).scalar_one_or_none()


@bot.inline_handler(lambda query: query.query.startswith("items;"))
async def get_items(query: types.InlineQuery):
    data = query.query.split(";")
    if len(data) == 4:
        server_id = data[1]
        search = data[2]
        filter_type = data[3].lower()
        await bot.answer_inline_query(query.id,
                                      await gen_items_result(await get_server(server_id), search, filter_type),
                                      cache_time=1)
    else:
        await bot.answer_inline_query(query.id, [], cache_time=1)


async def get_user(message: types.Message | int) -> User | None:
    async with session() as s:
        tg_id = message
        if isinstance(message, types.Message):
            tg_id = message.from_user.id
        return (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()


@bot.callback_query_handler(lambda call: call.data.startswith("buy"))
async def buy_callback(call: types.CallbackQuery, server_id: int = None):
    if call.message.from_user.id in users_temp:
        del users_temp[call.message.from_user.id]
    if server_id is None:
        server_id = int(call.data.split(";")[1])
    server = await get_server(server_id)
    user = await get_user(call.from_user.id)
    orders = list(
        filter(lambda order: order.status != "closed", user.orders[server.id] if server.id in user.orders else []))
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(f"Заказы{' ' + (len(orders)) if len(orders) > 0 else ''}",
                                   switch_inline_query_current_chat=f"orders;{server.id}"))
    markup.add(
        types.InlineKeyboardButton(f"Поиск предметов",
                                   switch_inline_query_current_chat=f"items;{server.id};название предмета;фильтр(рейтинг, цена, кол-во)"))
    markup.add(
        types.InlineKeyboardButton(f"Загрузить .litematic файл", callback_data=f"litematic;{server.id}"))
    cards_count = len(list(set(user.linked_cards[server.id]))) if server.id in user.linked_cards else 0
    if cards_count == 0:
        markup.add(
            types.InlineKeyboardButton(f"Привязать карту", callback_data=f"link_card;{server.id}"))
    else:
        markup.add(
            types.InlineKeyboardButton(f"Мои карты ({cards_count})", callback_data=f"link_card;{server.id}"))
    server_cart = user.cart[str(server.id)] if str(server.id) in user.cart else {}
    server_cart_count = 0
    for items in server_cart.values():
        server_cart_count += len(items.keys())
    if server_cart_count > 0:
        markup.add(
            types.InlineKeyboardButton(f"Корзина ({server_cart_count})",
                                       switch_inline_query_current_chat=f"cart;{server.id}"))
    await bot.edit_message_text(
        f"Выберите действие на сервере {server.server_name}.\nПри поиске предметов замените значения на необходимые.",
        call.message.chat.id,
        call.message.message_id, reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.via_bot is not None and message.via_bot.id == bot.user.id and (message.text.startswith(
        "Я хочу заказать") or message.text.startswith("I want to order")))
async def item_info(message: types.Message):
    if message.from_user.id in users_temp:
        del users_temp[message.from_user.id]
    data = message.text.split(" ")
    data = data[len(data) - 1].split(";")
    item_id = int(data[0])
    filter_type = data[1]
    item = await get_item(item_id)

    msg = await bot.reply_to(message, "Отправьте количетсво ресурсов для покупки")
    users_temp[message.from_user.id] = {"item": item, "filter_type": filter_type, "state": "amount", "auto_order": True,
                                        "message": msg}


@bot.message_handler(func=lambda message: message.via_bot is not None and message.via_bot.id == bot.user.id)
async def select_server(message: types.Message):
    if message.from_user.id in users_temp:
        del users_temp[message.from_user.id]
    is_server, server = await message_is_server_name(message)
    user = await get_user(message)
    if not is_server:
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Покупка", callback_data=f"buy;{server.id}"))
    server_cart = user.cart[str(server.id)] if str(server.id) in user.cart else {}
    server_cart_count = 0
    for items in server_cart.values():
        server_cart_count += len(items.keys())
    if server_cart_count > 0:
        markup.add(
            types.InlineKeyboardButton(f"Корзина ({server_cart_count})",
                                       switch_inline_query_current_chat=f"cart;{server.id}"))
    markup.add(types.InlineKeyboardButton("Пополнить баланс", callback_data=f"balance;{server.id}"))
    if len(user.shops) > 0:
        markup.add(types.InlineKeyboardButton(f"Мои магазины ({len(user.shops)})", callback_data=f"shops;{server.id}"))
    else:
        markup.add(types.InlineKeyboardButton("Открыть свой магазин", callback_data=f"create_shop;{server.id}"))
    await bot.send_message(message.chat.id, f"Выберите действие на сервере {server.server_name}", reply_markup=markup)


async def gen_message(message: types.Message, user_id: int):
    amount = users_temp[user_id]["amount"]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Изменить количество", callback_data=f"change_amount;{user_id}"))
    item: Item = users_temp[user_id]["item"]
    item = await get_item(item.id)
    add_text = ""
    if amount > item.amount:
        markup.add(types.InlineKeyboardButton(
            f"Автоматически дозаказать: {'✅' if users_temp[user_id]['auto_order'] else '❌'}",
            callback_data="change_auto_order"))
        add_text += "\nВнимание! Количество, заказанное вами, отсутствует у продавца, система может сама подобрать выгодные предложения, необходимые, чтобы заказать полный объём ресурсов."
    markup.add(types.InlineKeyboardButton("✅ Добавить в корзину", callback_data=f"add_to_cart;{user_id}"))

    await bot.edit_message_text(
        f"Заказанное количество: {amount}\nОбщая стоимость: {round(item.price / item.min_amount * amount, 0)} {(await get_mc_item(item.currency)).ru_name.lower()}" + add_text,
        users_temp[user_id]["message"].chat.id, users_temp[user_id]["message"].message_id,
        reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "change_amount")
async def change_amount(call: types.CallbackQuery):
    users_temp[call.message.from_user.id]["state"] = "amount"
    await bot.edit_message_text("Отправьте количетсво ресурсов для покупки", call.message.chat.id,
                                call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_auto_order"))
async def change_auto_order(call: types.CallbackQuery):
    user_id = int(call.data.split(";")[1])
    users_temp[user_id]["auto_order"] = not users_temp[user_id]["auto_order"]
    await gen_message(call.message, user_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cart"))
async def add_to_cart(call: types.CallbackQuery):
    user_id = int(call.data.split(";")[1])
    item = users_temp[user_id]["item"]
    user = await get_user(user_id)
    cart = user.cart
    if item.server_id not in cart: cart[item.server_id] = {}
    if item.shop_id not in cart[item.server_id]: cart[item.server_id][item.shop_id] = {}
    cart[item.server_id][item.shop_id][item.id] = users_temp[user_id]["amount"]
    async with session() as s:
        await s.execute(update(User).where(User.id == user.id).values({User.cart: cart}))
        try:
            await s.commit()
            del users_temp[user_id]
            await buy_callback(call, item.server_id)
        except:
            await s.rollback()


@bot.message_handler(func=lambda message: message.from_user.id in users_temp)
async def edit_amount(message: types.Message):
    if users_temp[message.from_user.id]["state"] != "amount": return
    try:
        users_temp[message.from_user.id]["state"] = "correcting"
        amount = int(message.text)
        item: Item = users_temp[message.from_user.id]["item"]
        if item.sell_type == "piece":
            if amount < item.min_amount:
                amount = item.min_amount
        elif item.sell_type == "stack":
            if amount % item.min_amount != 0:
                amount = item.min_amount * math.ceil(amount / item.amount)
        users_temp[message.from_user.id]["amount"] = amount
        await gen_message(users_temp[message.from_user.id]['message'], message.from_user.id)
    except ValueError:
        await bot.reply_to(message, "Количество блоков некорректное!\nОтправьте мне число блоков.")


async def main():
    await create_tables()
    await bot.polling(non_stop=True, skip_pending=True)


asyncio.run(main())
