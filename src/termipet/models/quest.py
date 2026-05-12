"""任务与成就 ORM 模型"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship

from termipet.database import Base


def _now():
    return datetime.now(timezone.utc)


# ── 任务定义（运行时数据） ────────────────────────────────────────────────────
QUEST_DEFINITIONS: dict[str, dict] = {
    # key: {name, desc, type, target_count, reward_coins, reward_stardust, reward_items}
    "daily_feed":      {"name": "今日喂食",     "type": "daily",  "desc": "今天喂食宠物 3 次",       "target": 3,  "coins": 20,  "stardust": 0, "items": []},
    "daily_play":      {"name": "快乐时光",     "type": "daily",  "desc": "今天玩耍 2 次",           "target": 2,  "coins": 15,  "stardust": 0, "items": []},
    "daily_clean":     {"name": "爱干净",       "type": "daily",  "desc": "今天清洁宠物 1 次",       "target": 1,  "coins": 10,  "stardust": 0, "items": []},
    "daily_adventure": {"name": "出发冒险",     "type": "daily",  "desc": "今天进行 1 次探险",       "target": 1,  "coins": 30,  "stardust": 1, "items": []},
    "weekly_craft":    {"name": "工匠之心",     "type": "weekly", "desc": "本周制作物品 5 次",       "target": 5,  "coins": 80,  "stardust": 3, "items": ["布料"]},
    "weekly_maze5":    {"name": "深渊探索者",   "type": "weekly", "desc": "本周探险到达第 5 层",     "target": 1,  "coins": 100, "stardust": 5, "items": ["稀有宝箱"]},
    "weekly_bond":     {"name": "心灵相通",     "type": "weekly", "desc": "本周亲密度提升 20 点",    "target": 20, "coins": 60,  "stardust": 2, "items": []},
}

ACHIEVEMENT_DEFINITIONS: dict[str, dict] = {
    # type: story/cumulative/hidden
    "first_adopt":      {"name": "初次领养",     "type": "story",     "desc": "领养了第一只灵兽",               "target": 1,  "stardust": 5,  "hidden": False},
    "first_adventure":  {"name": "踏上旅途",     "type": "story",     "desc": "第一次进入迷宫",                 "target": 1,  "stardust": 3,  "hidden": False},
    "stage_adult":      {"name": "成年礼",       "type": "story",     "desc": "宠物成长至成年阶段",             "target": 1,  "stardust": 10, "hidden": False},
    "stage_legend":     {"name": "传奇降临",     "type": "story",     "desc": "宠物成长至传奇阶段",             "target": 1,  "stardust": 50, "hidden": False},
    "stage_ancient":    {"name": "远古觉醒",     "type": "story",     "desc": "宠物成长至远古阶段",             "target": 1,  "stardust": 100,"hidden": False},
    "feed_100":         {"name": "百次喂食",     "type": "cumulative","desc": "累计喂食 100 次",               "target": 100,"stardust": 20, "hidden": False},
    "adventure_50":     {"name": "经验丰富",     "type": "cumulative","desc": "累计完成 50 次探险",             "target": 50, "stardust": 30, "hidden": False},
    "maze_floor10":     {"name": "深渊十层",     "type": "cumulative","desc": "探险到达第 10 层",               "target": 10, "stardust": 40, "hidden": False},
    "full_skills":      {"name": "全技能",       "type": "cumulative","desc": "学习所有通用技能",               "target": 8,  "stardust": 50, "hidden": False},
    "rich_1000":        {"name": "小富翁",       "type": "cumulative","desc": "金币达到 1000",                  "target": 1000,"stardust":15, "hidden": False},
    "health_0":         {"name": "大难不死",     "type": "hidden",    "desc": "健康值降至 0 后恢复",            "target": 1,  "stardust": 20, "hidden": True},
    "night_adventure":  {"name": "夜枭",         "type": "hidden",    "desc": "在午夜 12 点进行探险",           "target": 1,  "stardust": 15, "hidden": True},
    "craft_legend":     {"name": "传奇工匠",     "type": "hidden",    "desc": "制作出传说级物品",               "target": 1,  "stardust": 60, "hidden": True},
}


class Quest(Base):
    """宠物任务进度"""
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    quest_key = Column(String(64), nullable=False)
    progress = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    claimed = Column(Boolean, default=False)
    reset_at = Column(DateTime, nullable=True)  # 下次重置时间

    pet = relationship("Pet", back_populates="quests")

    @property
    def definition(self) -> dict:
        return QUEST_DEFINITIONS.get(self.quest_key, {})


class Achievement(Base):
    """宠物成就"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    achievement_key = Column(String(64), nullable=False)
    progress = Column(Float, default=0.0)
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)

    pet = relationship("Pet", back_populates="achievements")

    @property
    def definition(self) -> dict:
        return ACHIEVEMENT_DEFINITIONS.get(self.achievement_key, {})
