"""宠物与物种 ORM 模型"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from termipet.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Species(Base):
    """物种定义（静态数据表）"""
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    key = Column(String(32), unique=True, nullable=False)   # e.g. "cat"
    name_zh = Column(String(32), nullable=False)            # e.g. "猫型灵兽"
    description = Column(Text, default="")
    ascii_art_key = Column(String(32), default="cat")       # ascii_library 中的键名

    # 基础属性初始值（0-100）
    init_hunger = Column(Float, default=70.0)
    init_happiness = Column(Float, default=70.0)
    init_cleanliness = Column(Float, default=80.0)
    init_health = Column(Float, default=80.0)
    init_energy = Column(Float, default=70.0)
    init_intelligence = Column(Float, default=50.0)
    init_bond = Column(Float, default=20.0)
    init_constitution = Column(Float, default=60.0)

    # 属性成长率（1.0 = 普通）
    hunger_decay = Column(Float, default=1.0)
    happiness_decay = Column(Float, default=1.0)
    cleanliness_decay = Column(Float, default=0.8)
    energy_decay = Column(Float, default=1.0)

    # 专属技能树 JSON list[str]
    skill_tree_json = Column(Text, default="[]")

    # 天赋池 JSON list[str]
    talent_pool_json = Column(Text, default="[]")

    @property
    def skill_tree(self) -> list[str]:
        return json.loads(self.skill_tree_json or "[]")

    @property
    def talent_pool(self) -> list[str]:
        return json.loads(self.talent_pool_json or "[]")

    pets = relationship("Pet", back_populates="species_obj")


class Pet(Base):
    """宠物实体"""
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    species_key = Column(String(32), ForeignKey("species.key"), nullable=False)
    personality = Column(String(32), default="calm")
    talent = Column(String(64), default="")
    stage = Column(String(16), default="egg")    # egg/youth/teen/adult/peak/legend/ancient
    age_days = Column(Float, default=0.0)
    experience = Column(Float, default=0.0)
    skill_points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)   # 当前活跃宠物

    # ── 核心属性（0.0 ~ 100.0）──────────────────────────────────────────────
    hunger = Column(Float, default=70.0)        # 饱腹度
    happiness = Column(Float, default=70.0)     # 快乐值
    cleanliness = Column(Float, default=80.0)   # 清洁度
    health = Column(Float, default=80.0)        # 健康值
    energy = Column(Float, default=70.0)        # 精力
    intelligence = Column(Float, default=50.0)  # 智力
    bond = Column(Float, default=20.0)          # 亲密度
    constitution = Column(Float, default=60.0)  # 体质

    # ── 资源 ────────────────────────────────────────────────────────────────
    coins = Column(Integer, default=100)
    stardust = Column(Integer, default=0)

    # ── 时间戳 ──────────────────────────────────────────────────────────────
    born_at = Column(DateTime, default=_now)
    last_updated = Column(DateTime, default=_now)   # 上次属性衰减计算时间
    last_fed = Column(DateTime, nullable=True)
    last_played = Column(DateTime, nullable=True)
    last_cleaned = Column(DateTime, nullable=True)
    last_slept = Column(DateTime, nullable=True)

    # ── 装备 JSON {slot: item_id} ──────────────────────────────────────────
    equipped_items_json = Column(Text, default="{}")

    # ── 迷宫进度（当前探险状态快照） ────────────────────────────────────────
    current_maze_progress = Column(Text, default="{}")

    # ── 关系 ────────────────────────────────────────────────────────────────
    species_obj = relationship("Species", back_populates="pets")
    home = relationship("Home", back_populates="pet", uselist=False)
    skills = relationship("Skill", back_populates="pet", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="pet", cascade="all, delete-orphan")
    quests = relationship("Quest", back_populates="pet", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="pet", cascade="all, delete-orphan")
    maze_state = relationship("MazeState", back_populates="pet", uselist=False, cascade="all, delete-orphan")
    story_fragments = relationship("StoryFragment", back_populates="pet", cascade="all, delete-orphan")
    daily_event_logs = relationship("DailyEventLog", back_populates="pet", cascade="all, delete-orphan")

    # ── 属性便利方法 ─────────────────────────────────────────────────────────
    @property
    def equipped_items(self) -> dict[str, int]:
        return json.loads(self.equipped_items_json or "{}")

    @equipped_items.setter
    def equipped_items(self, val: dict[str, int]):
        self.equipped_items_json = json.dumps(val, ensure_ascii=False)

    @property
    def maze_progress(self) -> dict:
        return json.loads(self.current_maze_progress or "{}")

    @maze_progress.setter
    def maze_progress(self, val: dict):
        self.current_maze_progress = json.dumps(val, ensure_ascii=False)

    # ── 阶段系统 ─────────────────────────────────────────────────────────────
    STAGES = ["egg", "youth", "teen", "adult", "peak", "legend", "ancient"]
    STAGE_THRESHOLDS = {
        "egg": 0,
        "youth": 1,
        "teen": 7,
        "adult": 30,
        "peak": 90,
        "legend": 180,
        "ancient": 365,
    }

    def compute_stage(self) -> str:
        """根据年龄天数计算应处于的阶段"""
        stage = "egg"
        for s, days in self.STAGE_THRESHOLDS.items():
            if self.age_days >= days:
                stage = s
        return stage

    def stat_summary(self) -> dict[str, Any]:
        """返回所有属性的 dict（方便传给 UI）"""
        return {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "cleanliness": self.cleanliness,
            "health": self.health,
            "energy": self.energy,
            "intelligence": self.intelligence,
            "bond": self.bond,
            "constitution": self.constitution,
        }

    def __repr__(self) -> str:
        return f"<Pet {self.name!r} [{self.species_key}/{self.stage}]>"
