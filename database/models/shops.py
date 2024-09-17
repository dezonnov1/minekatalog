from sqlalchemy import Column, Integer, BigInteger, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from ..model_base import Base


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    item_id = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    min_amount = Column(Integer, nullable=False)
    sell_type = Column(Text, nullable=False, default="piece")
    data = Column(JSON, nullable=False, default={})
    hide = Column(Boolean, nullable=False, default=False)
    shop_id = Column(Integer, ForeignKey("shops.id"))


class Server(Base):
    __tablename__ = 'servers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    server_name = Column(Text, nullable=False)
    domain = Column(Text, nullable=False)
    currency = Column(Text, nullable=False)
    currency_rod = Column(Text, nullable=False)
    shops = relationship("Shop", uselist=True, lazy="subquery")


class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_name = Column(Text, nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    mc_nickname = Column(Text, nullable=False)
    shop_position = Column(JSON, nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"))
    available_items = relationship("Item", uselist=True, lazy="subquery")
    working = Column(Boolean, nullable=False, default=False)
    work_time = Column(JSON, nullable=False)
    subscribe_paid = Column(Boolean, nullable=False)
