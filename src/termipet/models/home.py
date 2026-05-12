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
            "卧室": self.bedroom_level,
            "厨房": self.kitchen_level,
            "工坊": self.workshop_level,
            "花园": self.garden_level,
            "图书室": self.library_level,
        }

    ROOM_KEYS = {
        "卧室": "bedroom_level",
        "厨房": "kitchen_level",
        "工坊": "workshop_level",
        "花园": "garden_level",
        "图书室": "library_level",
        "bedroom": "bedroom_level",
        "kitchen": "kitchen_level",
        "workshop": "workshop_level",
        "garden": "garden_level",
        "library": "library_level",
    }

    UPGRADE_COSTS = {
        # room_key: {level: (coins, {item_name: qty})}
        # 使用与 seeds.py 物品名完全一致的名称
        "bedroom_level":  {
            1: (0, {}),
            2: (50,  {"皮革": 2}),
            3: (150, {"皮革": 5, "数据碎片": 1}),
            4: (300, {"数据碎片": 3}),
            5: (600, {"魔法水晶": 1}),
        },
        "kitchen_level":  {
            1: (0, {}),
            2: (60,  {"铁锭": 2}),
            3: (180, {"铁锭": 3, "数据碎片": 1}),
            4: (350, {"数据碎片": 3, "魔法粉末": 2}),
            5: (700, {"魔法水晶": 1}),
        },
        "workshop_level": {
            0: (0, {}),
            1: (80,  {"铁锭": 3, "皮革": 2}),
            2: (200, {"铁锭": 5, "数据碎片": 2}),
            3: (400, {"数据碎片": 5, "魔法粉末": 2}),
            4: (800, {"魔法水晶": 2}),
            5: (1500, {"魔法水晶": 5}),
        },
        "garden_level":   {
            0: (0, {}),
            1: (50,  {"皮革": 3}),
            2: (120, {"草药": 5, "数据碎片": 1}),
            3: (250, {"数据碎片": 3, "魔法粉末": 1}),
            4: (500, {"魔法水晶": 1}),
            5: (1000, {"魔法水晶": 3}),
        },
        "library_level":  {
            0: (0, {}),
            1: (100, {"纸张": 5, "墨水": 3}),
            2: (250, {"纸张": 10, "数据碎片": 2}),
            3: (500, {"数据碎片": 5, "魔法粉末": 3}),
            4: (1000, {"魔法水晶": 2}),
            5: (2000, {"魔法水晶": 5, "星辰金属": 1}),
        },
    }
