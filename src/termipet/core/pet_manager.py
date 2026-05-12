"""宠物管理器 — 属性衰减、成长、互动核心逻辑"""
from __future__ import annotations

import random
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from termipet.models.pet import Pet, Species
from termipet.models.home import Home
from termipet.models.item import Item, Inventory
from termipet.models.quest import Quest, Achievement, QUEST_DEFINITIONS, ACHIEVEMENT_DEFINITIONS
from termipet.models.story import StoryFragment, STORY_FRAGMENTS
from termipet import config as cfg


# ── 衰减系数（每小时） ────────────────────────────────────────────────────────
BASE_DECAY = {
    "hunger":       4.0,   # 饱腹每小时减少 4 点
    "happiness":    2.5,
    "cleanliness":  1.5,
    "energy":       3.0,
}

PERSONALITY_MODIFIERS = {
    # personality: {stat: multiplier}
    "勇敢":   {"happiness": 0.8, "energy": 1.2},
    "胆小":   {"happiness": 1.3, "energy": 0.9},
    "顽皮":   {"happiness": 0.7, "hunger": 1.3},
    "沉稳":   {"hunger": 0.9,   "energy": 0.9},
    "温柔":   {"cleanliness": 0.7, "happiness": 0.85},
    "傲娇":   {"bond": 0.5},
}

TALENT_EFFECTS = {
    "大胃王":   {"hunger_decay": 1.5},
    "探险家":   {"adventure_exp": 1.5},
    "甜睡者":   {"energy_recovery": 1.5},
    "社交达人": {"bond_gain": 1.5},
    "铁胃":     {"hunger_decay": 0.7},
    "自愈力":   {"health_recovery": 1.3},
    "天才儿童": {"intelligence_growth": 2.0},
    "夜猫子":   {"night_activity": 1.5},
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PetManager:
    """宠物管理器 — 所有宠物操作的入口"""

    def __init__(self, session: Session):
        self.session = session

    # ── 获取活跃宠物 ──────────────────────────────────────────────────────────
    def get_active_pet(self) -> Optional[Pet]:
        return self.session.query(Pet).filter_by(is_active=True).first()

    def require_active_pet(self) -> Pet:
        """获取活跃宠物，不存在则抛出 ValueError"""
        pet = self.get_active_pet()
        if pet is None:
            raise ValueError("还没有宠物！请先使用 [bold cyan]pet adopt[/] 命令领养一只灵兽。")
        return pet

    # ── 领养 ──────────────────────────────────────────────────────────────────
    def adopt(self, species_key: str, name: str) -> Pet:
        """领养新宠物"""
        # 验证物种
        species = self.session.query(Species).filter_by(key=species_key).first()
        if species is None:
            available = [s.key for s in self.session.query(Species).all()]
            raise ValueError(
                f"未知物种 '{species_key}'。\n可用物种：{', '.join(available) or '暂无数据，请先初始化游戏数据'}"
            )

        # 验证名字
        name = name.strip()
        if not name:
            raise ValueError("宠物名字不能为空！")
        if len(name) > 20:
            raise ValueError("宠物名字不能超过 20 个字符！")

        # 将现有宠物设为非活跃
        existing = self.session.query(Pet).filter_by(is_active=True).first()
        if existing:
            existing.is_active = False

        # 随机性格与天赋
        personalities = ["勇敢", "胆小", "顽皮", "沉稳", "温柔", "傲娇"]
        talent_pool = species.talent_pool or list(TALENT_EFFECTS.keys())
        personality = random.choice(personalities)
        talent = random.choice(talent_pool) if talent_pool else random.choice(list(TALENT_EFFECTS.keys()))

        now = _utcnow()
        pet = Pet(
            name=name,
            species_key=species_key,
            personality=personality,
            talent=talent,
            stage="蛋",
            age_days=0.0,
            born_at=now,
            last_updated=now,
            hunger=species.init_hunger,
            happiness=species.init_happiness,
            cleanliness=species.init_cleanliness,
            health=species.init_health,
            energy=species.init_energy,
            intelligence=species.init_intelligence,
            bond=species.init_bond,
            constitution=species.init_constitution,
            coins=100,
            stardust=0,
            is_active=True,
        )
        self.session.add(pet)
        self.session.flush()

        # 创建家园
        home = Home(pet_id=pet.id)
        self.session.add(home)

        # 初始化任务
        self._init_quests(pet)

        # 初始化成就
        self._init_achievements(pet)

        # 解锁序章故事
        self._unlock_story(pet, "prologue_1")

        self.session.commit()
        return pet

    # ── 属性衰减 ─────────────────────────────────────────────────────────────
    def apply_decay(self, pet: Pet) -> dict[str, float]:
        """根据距上次更新的时间差计算并应用属性衰减，返回各属性减少量"""
        now = _utcnow()
        last = pet.last_updated
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)

        elapsed_hours = (now - last).total_seconds() / 3600.0
        # 防止极端值（超过7天的离线时间上限7天计算）
        elapsed_hours = min(elapsed_hours, 168.0)
        if elapsed_hours < 0.001:
            return {}

        species = pet.species_obj
        multiplier = cfg.get("decay_multiplier", 1.0)
        deltas: dict[str, float] = {}

        def _decay(stat: str, base: float, species_mult: float = 1.0):
            pers_mult = PERSONALITY_MODIFIERS.get(pet.personality, {}).get(stat, 1.0)
            talent_mult = 1.0
            if pet.talent in TALENT_EFFECTS:
                talent_mult = TALENT_EFFECTS[pet.talent].get(f"{stat}_decay", 1.0)
            delta = base * species_mult * pers_mult * talent_mult * multiplier * elapsed_hours
            deltas[stat] = -delta
            return delta

        # 计算各属性衰减
        hunger_loss = _decay("hunger", BASE_DECAY["hunger"], species.hunger_decay if species else 1.0)
        happiness_loss = _decay("happiness", BASE_DECAY["happiness"], species.happiness_decay if species else 1.0)
        cleanliness_loss = _decay("cleanliness", BASE_DECAY["cleanliness"], species.cleanliness_decay if species else 1.0)
        energy_loss = _decay("energy", BASE_DECAY["energy"], species.energy_decay if species else 1.0)

        # 饥饿 & 快乐影响健康
        health_penalty = 0.0
        if pet.hunger < 20:
            health_penalty += (20 - pet.hunger) * 0.1 * elapsed_hours
        if pet.happiness < 20:
            health_penalty += (20 - pet.happiness) * 0.05 * elapsed_hours

        # 应用
        pet.hunger = max(0.0, pet.hunger - hunger_loss)
        pet.happiness = max(0.0, pet.happiness - happiness_loss)
        pet.cleanliness = max(0.0, pet.cleanliness - cleanliness_loss)
        pet.energy = max(0.0, pet.energy - energy_loss)
        pet.health = max(0.0, min(100.0, pet.health - health_penalty))

        # 更新年龄
        pet.age_days += elapsed_hours / 24.0

        # 检查阶段变化
        new_stage = pet.compute_stage()
        if new_stage != pet.stage:
            old_stage = pet.stage
            pet.stage = new_stage
            self._on_stage_change(pet, old_stage, new_stage)

        pet.last_updated = now
        return deltas

    # ── 互动操作 ─────────────────────────────────────────────────────────────
    def feed(self, pet: Pet, item_key: Optional[str] = None) -> dict:
        """喂食"""
        self.apply_decay(pet)

        if item_key:
            # 使用指定食物
            inv_entry = (
                self.session.query(Inventory)
                .join(Item)
                .filter(Inventory.pet_id == pet.id)
                .filter(Item.key == item_key)
                .filter(Inventory.quantity > 0)
                .first()
            )
            if inv_entry is None:
                # 尝试模糊匹配
                inv_entry = (
                    self.session.query(Inventory)
                    .join(Item)
                    .filter(Inventory.pet_id == pet.id)
                    .filter(Item.name.contains(item_key))
                    .filter(Inventory.quantity > 0)
                    .first()
                )
            if inv_entry is None:
                raise ValueError(f"背包中没有 '{item_key}'，请先购买或制作。")
            item = inv_entry.item
            if item.item_type not in ("consumable", "food"):
                raise ValueError(f"'{item.name}' 不是食物，无法喂给宠物。")

            effects = item.effects
            for stat, val in effects.items():
                self._apply_stat(pet, stat, val)

            inv_entry.quantity -= 1
            if inv_entry.quantity <= 0:
                self.session.delete(inv_entry)

            result = {"item": item.name, "effects": effects}
        else:
            # 普通喂食（使用内置食物）
            hunger_gain = random.uniform(20, 30)
            health_gain = random.uniform(2, 5)
            pet.hunger = min(100.0, pet.hunger + hunger_gain)
            pet.health = min(100.0, pet.health + health_gain)
            result = {"item": "普通饲料", "effects": {"饱腹": hunger_gain, "健康": health_gain}}

        pet.last_fed = _utcnow()
        self._update_quest_progress(pet, "daily_feed", 1)
        self._update_achievement_progress(pet, "feed_100", 1)
        self.session.commit()
        return result

    def play(self, pet: Pet) -> dict:
        """玩耍"""
        self.apply_decay(pet)

        if pet.energy < 10:
            raise ValueError(f"{pet.name} 太累了，精力只剩 {pet.energy:.0f}！先让它休息吧。")

        energy_cost = random.uniform(8, 15)
        happiness_gain = random.uniform(15, 25)
        bond_gain = random.uniform(1, 3)

        # 性格调整
        if pet.personality == "顽皮":
            happiness_gain *= 1.3
        elif pet.personality == "傲娇":
            happiness_gain *= 0.7
            bond_gain *= 1.5  # 傲娇的亲密度成长更快

        pet.energy = max(0.0, pet.energy - energy_cost)
        pet.happiness = min(100.0, pet.happiness + happiness_gain)
        pet.bond = min(100.0, pet.bond + bond_gain)
        pet.last_played = _utcnow()

        self._update_quest_progress(pet, "daily_play", 1)
        self._update_quest_progress(pet, "weekly_bond", int(bond_gain))
        self.session.commit()

        return {"happiness_gain": happiness_gain, "bond_gain": bond_gain, "energy_cost": energy_cost}

    def clean(self, pet: Pet) -> dict:
        """清洁"""
        self.apply_decay(pet)

        cleanliness_gain = random.uniform(30, 50)
        happiness_gain = random.uniform(3, 8)

        pet.cleanliness = min(100.0, pet.cleanliness + cleanliness_gain)
        pet.happiness = min(100.0, pet.happiness + happiness_gain)
        pet.last_cleaned = _utcnow()

        self._update_quest_progress(pet, "daily_clean", 1)
        self.session.commit()

        return {"cleanliness_gain": cleanliness_gain, "happiness_gain": happiness_gain}

    def sleep(self, pet: Pet, hours: float) -> dict:
        """睡觉"""
        self.apply_decay(pet)

        hours = max(0.5, min(hours, 12.0))   # 0.5~12小时

        energy_gain = hours * 8.0
        health_gain = hours * 2.0
        hunger_loss = hours * 1.5   # 睡觉也会饿

        pet.energy = min(100.0, pet.energy + energy_gain)
        pet.health = min(100.0, pet.health + health_gain)
        pet.hunger = max(0.0, pet.hunger - hunger_loss)
        pet.last_slept = _utcnow()

        self.session.commit()
        return {"energy_gain": energy_gain, "health_gain": health_gain, "hours": hours}

    # ── 货币 ──────────────────────────────────────────────────────────────────
    def add_coins(self, pet: Pet, amount: int, reason: str = "") -> None:
        pet.coins = max(0, pet.coins + amount)

    def add_stardust(self, pet: Pet, amount: int) -> None:
        pet.stardust = max(0, pet.stardust + amount)

    def spend_coins(self, pet: Pet, amount: int) -> None:
        if pet.coins < amount:
            raise ValueError(f"金币不足！需要 {amount} 金币，当前只有 {pet.coins} 金币。")
        pet.coins -= amount

    def spend_stardust(self, pet: Pet, amount: int) -> None:
        if pet.stardust < amount:
            raise ValueError(f"星尘不足！需要 {amount} 星尘，当前只有 {pet.stardust} 星尘。")
        pet.stardust -= amount

    # ── 内部工具 ─────────────────────────────────────────────────────────────
    def _apply_stat(self, pet: Pet, stat: str, value: float) -> None:
        """安全地修改宠物属性"""
        STAT_MAP = {
            "hunger": "hunger", "饱腹": "hunger",
            "happiness": "happiness", "快乐": "happiness",
            "cleanliness": "cleanliness", "清洁": "cleanliness",
            "health": "health", "健康": "health",
            "energy": "energy", "精力": "energy",
            "intelligence": "intelligence", "智力": "intelligence",
            "bond": "bond", "亲密": "bond",
            "constitution": "constitution", "体质": "constitution",
        }
        attr = STAT_MAP.get(stat)
        if attr:
            cur = getattr(pet, attr, 0.0)
            setattr(pet, attr, max(0.0, min(100.0, cur + value)))

    def _on_stage_change(self, pet: Pet, old: str, new: str) -> None:
        """阶段变化处理：奖励技能点、解锁故事"""
        stage_rewards = {
            "幼年": (1, "growth_1"),
            "少年": (2, "growth_2"),
            "成年": (3, "growth_3"),
            "巅峰": (3, None),
            "传奇": (5, "growth_4"),
            "远古": (10, None),
        }
        reward = stage_rewards.get(new)
        if reward:
            sp, story_key = reward
            pet.skill_points += sp
            if story_key:
                self._unlock_story(pet, story_key)

        # 成就检查
        if new == "成年":
            self._unlock_achievement(pet, "stage_adult")
        elif new == "传奇":
            self._unlock_achievement(pet, "stage_legend")
        elif new == "远古":
            self._unlock_achievement(pet, "stage_ancient")

    def _unlock_story(self, pet: Pet, key: str) -> None:
        if key not in STORY_FRAGMENTS:
            return
        existing = self.session.query(StoryFragment).filter_by(pet_id=pet.id, fragment_key=key).first()
        if not existing:
            frag = StoryFragment(pet_id=pet.id, fragment_key=key)
            self.session.add(frag)

    def _init_quests(self, pet: Pet) -> None:
        now = _utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        next_week = tomorrow + timedelta(days=7 - tomorrow.weekday())

        for key, defn in QUEST_DEFINITIONS.items():
            reset = next_week if defn["type"] == "weekly" else tomorrow
            q = Quest(pet_id=pet.id, quest_key=key, reset_at=reset)
            self.session.add(q)

    def _init_achievements(self, pet: Pet) -> None:
        for key in ACHIEVEMENT_DEFINITIONS:
            a = Achievement(pet_id=pet.id, achievement_key=key)
            self.session.add(a)

    def _update_quest_progress(self, pet: Pet, quest_key: str, delta: int) -> None:
        q = self.session.query(Quest).filter_by(pet_id=pet.id, quest_key=quest_key).first()
        if q and not q.completed:
            defn = q.definition
            q.progress = min(q.progress + delta, defn.get("target", 999))
            if q.progress >= defn.get("target", 999):
                q.completed = True

    def _update_achievement_progress(self, pet: Pet, ach_key: str, delta: float) -> None:
        a = self.session.query(Achievement).filter_by(pet_id=pet.id, achievement_key=ach_key).first()
        if a and not a.unlocked:
            defn = a.definition
            a.progress = min(a.progress + delta, defn.get("target", 9999))
            if a.progress >= defn.get("target", 9999):
                self._unlock_achievement(pet, ach_key)

    def _unlock_achievement(self, pet: Pet, ach_key: str) -> None:
        a = self.session.query(Achievement).filter_by(pet_id=pet.id, achievement_key=ach_key).first()
        if a and not a.unlocked:
            a.unlocked = True
            a.unlocked_at = _utcnow()
            defn = a.definition
            stardust = defn.get("stardust", 0)
            if stardust:
                pet.stardust += stardust
