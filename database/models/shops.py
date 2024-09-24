from sqlalchemy import Column, Integer, BigInteger, Text, ForeignKey, JSON, Boolean, Float, DateTime, UUID
from sqlalchemy.orm import relationship

from ..model_base import Base


class Enchantment(Base):
    __tablename__ = 'enchantments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    max_level = Column(Integer, nullable=False)
    ru_name = Column(Text, nullable=False)
    en_name = Column(Text, nullable=False)
    available_types = Column(JSON, nullable=False, default=[])
    disable = Column(JSON, nullable=False, default=[])


class MCItem(Base):
    __tablename__ = 'mc_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mc_id = Column(Text, nullable=False)
    ru_name = Column(Text, nullable=False)
    en_name = Column(Text, nullable=False)
    item_type = Column(Text, nullable=True)
    image_url = Column(Text, nullable=False)
    mod = Column(Boolean, nullable=False, default=False)
    max_durable = Column(Integer, nullable=False)
    category = Column(Text, nullable=False)


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    item_id = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    currency = Column(Integer, ForeignKey("mc_items.id"), nullable=False)
    item_currency = relationship("MCItem", uselist=False, lazy="subquery", foreign_keys=[currency])
    amount = Column(Integer, nullable=False)
    min_amount = Column(Integer, nullable=False)
    sell_type = Column(Text, nullable=False, default="")
    data = Column(JSON, nullable=False, default={})
    hide = Column(Boolean, nullable=False, default=False)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    shop = relationship("Shop", uselist=False, lazy="subquery", back_populates="available_items")
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    server = relationship("Server", uselist=False, lazy="subquery", foreign_keys=[server_id])
    item_title = Column(Text, nullable=True)
    enchantments = Column(Text, nullable=True)
    durable = Column(Integer, nullable=False)


class Server(Base):
    __tablename__ = 'servers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_name = Column(Text, nullable=False)
    domain = Column(Text, nullable=False)
    currency = Column(Integer, ForeignKey("mc_items.id"), nullable=False)
    item_currency = relationship("MCItem", uselist=False, lazy="subquery", foreign_keys=[currency])
    logo = Column(Text, nullable=False)
    shops = relationship("Shop", uselist=True, lazy="subquery")
    items = relationship("Item", uselist=True, lazy="subquery", overlaps="server")


class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Text, nullable=True)
    shop_name = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", uselist=False, lazy="subquery", back_populates="shops")
    mc_nickname = Column(Text, nullable=False)
    shop_position = Column(JSON, nullable=False)
    rating = Column(Float, nullable=False, default=0)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    server = relationship("Server", uselist=False, lazy="subquery", back_populates="shops")
    available_items = relationship("Item", uselist=True, lazy="subquery")
    working = Column(Boolean, nullable=False, default=False)
    work_time = Column(JSON, nullable=False)
    subscribe_paid = Column(Boolean, nullable=False)
    available_promos = Column(JSON, nullable=False, default=[])
    api_token = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False)
    language = Column(Text, nullable=False, default="russian")
    balance = Column(JSON, nullable=False, default={})
    cart = Column(JSON, nullable=False, default={})
    linked_cards = Column(JSON, nullable=False, default={})
    token = Column(Text, nullable=False)
    expired_at = Column(DateTime, nullable=False)
    shops = relationship("Shop", uselist=True, lazy="subquery")
    orders = relationship("Order", uselist=True, lazy="subquery")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Text, nullable=False)
    user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_owner = relationship("User", foreign_keys=[user], lazy="subquery", uselist=False, overlaps="orders")
    status = Column(Text, nullable=False, default="created")
    ordered_items = Column(JSON, nullable=False, default={})
