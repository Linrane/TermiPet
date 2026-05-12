"""物品与背包 ORM 模型"""
from __future__ import annotations

import json
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from termipet.database import Base


class Item(Base):
    """物品定义（静态数据）"""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    item_type = Column(String(32), default="consumable")   # consumable/material/equipment/collectible
    rarity = Column(String(16), default="common")           # common/rare/legendary
    description = Column(Text, default="")

    # 效果 JSON {stat: delta, ...}
    effects_json = Column(Text, default="{}")

    buy_price = Column(Integer, default=10)
    sell_price = Column(Integer, default=5)

    # 装备槽（equipment 类型用）
    equip_slot = Column(String(32), nullable=True)   # neck/body/head/feet

    # 是否可购买
    in_shop = Column(Boolean, default=True)

    @property
    def effects(self) -> dict[str, float]:
        return json.loads(self.effects_json or "{}")

    @effects.setter
    def effects(self, val: dict):
        self.effects_json = json.dumps(val, ensure_ascii=False)

    inventory_entries = relationship("Inventory", back_populates="item")

    def __repr__(self) -> str:
        return f"<Item {self.name!r} [{self.rarity}]>"


class Inventory(Base):
    """宠物背包条目"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    equipped = Column(Boolean, default=False)

    pet = relationship("Pet", back_populates="inventory")
    item = relationship("Item", back_populates="inventory_entries")

    def __repr__(self) -> str:
        return f"<Inventory pet={self.pet_id} item={self.item_id} qty={self.quantity}>"
