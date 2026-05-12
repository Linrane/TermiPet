"""迷宫状态 ORM 模型"""
from __future__ import annotations

import json
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from termipet.database import Base

# ── 单元格类型常量（供迷宫系统和 UI 引用） ────────────────────────────────────
CELL_WALL   = "#"
CELL_FLOOR  = "."
CELL_START  = "S"
CELL_EXIT   = "E"
CELL_CHEST  = "C"
CELL_TRAP   = "T"
CELL_ENEMY  = "M"
CELL_PUZZLE = "?"
CELL_SHOP   = "$"
CELL_STORY  = "!"


class MazeState(Base):
    """当前进行中的迷宫状态（持久化存档）"""
    __tablename__ = "maze_states"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), unique=True, nullable=False)

    floor = Column(Integer, default=1)
    pos_x = Column(Integer, default=0)
    pos_y = Column(Integer, default=0)
    in_progress = Column(Boolean, default=False)   # 是否正在探险中

    # 完整地图 JSON（list of list of cell_type）
    map_json = Column(Text, default="[]")

    # 已探索格子 JSON set serialized as list
    explored_json = Column(Text, default="[]")

    # 临时增益 JSON {buff_name: {value, expires_floor}}
    temp_buffs_json = Column(Text, default="{}")

    # 迷宫内背包（临时物品，撤退后带回）
    loot_json = Column(Text, default="[]")

    pet = relationship("Pet", back_populates="maze_state")

    @property
    def maze_map(self) -> list[list[str]]:
        return json.loads(self.map_json or "[]")

    @maze_map.setter
    def maze_map(self, val: list):
        self.map_json = json.dumps(val, ensure_ascii=False)

    @property
    def explored(self) -> set[tuple[int, int]]:
        raw = json.loads(self.explored_json or "[]")
        return {tuple(p) for p in raw}

    @explored.setter
    def explored(self, val: set[tuple[int, int]]):
        self.explored_json = json.dumps([list(p) for p in val], ensure_ascii=False)

    @property
    def temp_buffs(self) -> dict:
        return json.loads(self.temp_buffs_json or "{}")

    @temp_buffs.setter
    def temp_buffs(self, val: dict):
        self.temp_buffs_json = json.dumps(val, ensure_ascii=False)

    @property
    def loot(self) -> list[dict]:
        return json.loads(self.loot_json or "[]")

    @loot.setter
    def loot(self, val: list):
        self.loot_json = json.dumps(val, ensure_ascii=False)
