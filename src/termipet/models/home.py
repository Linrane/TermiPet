"""家园 ORM 模型"""
from __future__ import annotations

import json
from sqlalchemy import Column, Integer, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from termipet.database import Base


class Home(Base):
    """宠物家园"""
    __tablename__ = "homes"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), unique=True, nullable=False)

    level = Column(Integer, default=1)
    decoration_score = Column(Float, default=0.0)

    # 各房间等级（1-5）
    bedroom_level = Column(Integer, default=1)     # 卧室 - 恢复精力
    kitchen_level = Column(Integer, default=1)     # 厨房 - 制作食物
    workshop_level = Column(Integer, default=0)    # 工坊 - 制作玩具/装备（解锁需升级）
    garden_level = Column(Integer, default=0)      # 花园 - 种植材料
    library_level = Column(Integer, default=0)     # 图书室 - 研究技能

    # 家具列表 JSON list[str]
    furniture_json = Column(Text, default="[]")

    # 花园种植槽 JSON list[{plant, planted_at, ready_at}]
    garden_slots_json = Column(Text, default="[]")

    pet = relationship("Pet", back_populates="home")

    @property
    def furniture(self) -> list[str]:
        return json.loads(self.furniture_json or "[]")

    @furniture.setter
    def furniture(self, val: list):
        self.furniture_json = json.dumps(val, ensure_ascii=False)

    @property
    def garden_slots(self) -> list[dict]:
        return json.loads(self.garden_slots_json or "[]")

    @garden_slots.setter
    def garden_slots(self, val: list):
        self.garden_slots_json = json.dumps(val, ensure_ascii=False)

    def room_status(self) -> dict[str, int]:
        return {
            "bedroom": self.bedroom_level,
            "kitchen": self.kitchen_level,
            "workshop": self.workshop_level,
            "garden": self.garden_level,
            "library": self.library_level,
        }

    ROOM_KEYS = {
        "bedroom": "bedroom_level",
        "kitchen": "kitchen_level",
        "workshop": "workshop_level",
        "garden": "garden_level",
        "library": "library_level",
    }

    UPGRADE_COSTS = {
        # room_key: {level: (coins, {item_key: qty})}
        "bedroom_level":  {
            1: (0, {}),
            2: (50,  {"leather": 2}),
            3: (150, {"leather": 5, "data_shard": 1}),
            4: (300, {"data_shard": 3}),
            5: (600, {"magic_crystal": 1}),
        },
        "kitchen_level":  {
            1: (0, {}),
            2: (60,  {"iron_ingot": 2}),
            3: (180, {"iron_ingot": 3, "data_shard": 1}),
            4: (350, {"data_shard": 3, "magic_powder": 2}),
            5: (700, {"magic_crystal": 1}),
        },
        "workshop_level": {
            0: (0, {}),
            1: (80,  {"iron_ingot": 3, "leather": 2}),
            2: (200, {"iron_ingot": 5, "data_shard": 2}),
            3: (400, {"data_shard": 5, "magic_powder": 2}),
            4: (800, {"magic_crystal": 2}),
            5: (1500, {"magic_crystal": 5}),
        },
        "garden_level":   {
            0: (0, {}),
            1: (50,  {"leather": 3}),
            2: (120, {"herb": 5, "data_shard": 1}),
            3: (250, {"data_shard": 3, "magic_powder": 1}),
            4: (500, {"magic_crystal": 1}),
            5: (1000, {"magic_crystal": 3}),
        },
        "library_level":  {
            0: (0, {}),
            1: (100, {"paper": 5, "ink": 3}),
            2: (250, {"paper": 10, "data_shard": 2}),
            3: (500, {"data_shard": 5, "magic_powder": 3}),
            4: (1000, {"magic_crystal": 2}),
            5: (2000, {"magic_crystal": 5, "star_metal": 1}),
        },
    }
