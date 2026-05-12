"""随机事件系统 — 互动触发与定时事件"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.item import Item, Inventory


# ── 随机事件定义 ──────────────────────────────────────────────────────────────
RANDOM_EVENTS = [
    {
        "key": "found_coin",
        "weight": 20,
        "title": "意外发现",
        "desc": "{name} 在角落里发现了几枚闪闪发光的金币！",
        "effect": {"coins": 15},
    },
    {
        "key": "found_material",
        "weight": 15,
        "title": "天降材料",
        "desc": "{name} 翻出了一些有用的材料碎片。",
        "effect": {"item": "data_shard", "qty": 1},
    },
    {
        "key": "happy_moment",
        "weight": 25,
        "title": "快乐时刻",
        "desc": "{name} 追着屏幕上的光标玩得不亦乐乎！",
        "effect": {"happiness": 10},
    },
    {
        "key": "energy_burst",
        "weight": 10,
        "title": "精力迸发",
        "desc": "{name} 突然精神抖擞，像是充了电一样！",
        "effect": {"energy": 15},
    },
    {
        "key": "bad_dream",
        "weight": 8,
        "title": "噩梦缠身",
        "desc": "{name} 睡觉时发出了奇怪的声音，看起来不太好受……",
        "effect": {"happiness": -10, "energy": -5},
    },
    {
        "key": "stomach_upset",
        "weight": 5,
        "title": "消化不良",
        "desc": "{name} 好像吃了什么不对劲的东西，肚子不舒服。",
        "effect": {"hunger": -15, "health": -5},
    },
    {
        "key": "skill_insight",
        "weight": 7,
        "title": "顿悟时刻",
        "desc": "{name} 突然有所感悟，技能点+1！",
        "effect": {"skill_points": 1},
    },
    {
        "key": "mystery_gift",
        "weight": 3,
        "title": "神秘礼物",
        "desc": "一个神秘的包裹出现在门口，里面有些特别的东西……",
        "effect": {"stardust": 2},
    },
]


class EventManager:
    def __init__(self, session: Session):
        self.session = session

    def maybe_trigger(self, pet: Pet, base_chance: float = 0.15) -> dict | None:
        """有概率触发随机事件，返回事件结果或 None"""
        # 幸运星技能加成
        lucky_bonus = 0.0
        for skill in pet.skills:
            from termipet.models.skill import SKILL_DEFINITIONS
            defn = SKILL_DEFINITIONS.get(skill.skill_key, {})
            lucky_bonus += defn.get("effect", {}).get("luck", 0.0) * skill.level

        if random.random() > base_chance + lucky_bonus:
            return None

        # 加权随机选择事件
        weights = [e["weight"] for e in RANDOM_EVENTS]
        event = random.choices(RANDOM_EVENTS, weights=weights)[0]

        result = self._apply_event(pet, event)
        self.session.commit()
        return result

    def _apply_event(self, pet: Pet, event: dict) -> dict:
        effect = event["effect"]

        if "coins" in effect:
            pet.coins += effect["coins"]
        if "stardust" in effect:
            pet.stardust += effect["stardust"]
        if "skill_points" in effect:
            pet.skill_points += effect["skill_points"]
        if "happiness" in effect:
            pet.happiness = max(0, min(100, pet.happiness + effect["happiness"]))
        if "energy" in effect:
            pet.energy = max(0, min(100, pet.energy + effect["energy"]))
        if "health" in effect:
            pet.health = max(0, min(100, pet.health + effect["health"]))
        if "hunger" in effect:
            pet.hunger = max(0, min(100, pet.hunger + effect["hunger"]))
        if "item" in effect:
            item = self.session.query(Item).filter_by(key=effect["item"]).first()
            if item:
                inv = self.session.query(Inventory).filter_by(pet_id=pet.id, item_id=item.id).first()
                if inv:
                    inv.quantity += effect.get("qty", 1)
                else:
                    inv = Inventory(pet_id=pet.id, item_id=item.id, quantity=effect.get("qty", 1))
                    self.session.add(inv)

        return {
            "key": event["key"],
            "title": event["title"],
            "desc": event["desc"].format(name=pet.name),
            "effect": effect,
        }
