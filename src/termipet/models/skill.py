"""技能 ORM 模型"""
from __future__ import annotations

import json
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from termipet.database import Base


# ── 全局技能定义（非 ORM，运行时数据） ──────────────────────────────────────
SKILL_DEFINITIONS: dict[str, dict] = {
    # 通用技能
    "quick_heal":    {"name": "急救",     "type": "治愈",   "cost": 1, "desc": "快速恢复少量健康值",          "effect": {"health": 15}},
    "treasure_nose": {"name": "寻宝鼻",   "type": "寻宝",   "cost": 2, "desc": "探险中更容易找到宝箱",        "effect": {"loot_rate": 0.2}},
    "comfort_song":  {"name": "安抚曲",   "type": "安抚",   "cost": 1, "desc": "安抚时额外恢复快乐值",        "effect": {"happiness": 20}},
    "battle_stance": {"name": "战斗姿态", "type": "战斗辅助", "cost": 2, "desc": "进入战斗时获得防御加成",    "effect": {"defense": 0.15}},
    "night_hunter":  {"name": "夜行者",   "type": "被动",   "cost": 2, "desc": "夜间探险获得双倍经验",        "effect": {"night_exp": 2.0}},
    "forager":       {"name": "觅食者",   "type": "被动",   "cost": 1, "desc": "每天自动获得少量食物材料",    "effect": {"daily_food": 1}},
    "sharp_mind":    {"name": "聪慧",     "type": "被动",   "cost": 2, "desc": "智力成长加速",                "effect": {"int_growth": 1.5}},
    "tough_skin":    {"name": "铁皮",     "type": "被动",   "cost": 1, "desc": "体质上限+10",                 "effect": {"constitution_max": 10}},
    "lucky_star":    {"name": "幸运星",   "type": "被动",   "cost": 3, "desc": "随机事件触发好结果概率+20%",  "effect": {"luck": 0.2}},
    # 猫型专属
    "shadow_step":   {"name": "影步",     "type": "探险",   "cost": 2, "desc": "陷阱触发率降低30%",          "effect": {"trap_evade": 0.3}, "species": ["cat"]},
    "purr_therapy":  {"name": "呼噜疗愈", "type": "治愈",   "cost": 1, "desc": "睡眠期间健康恢复额外+10",    "effect": {"sleep_heal": 10}, "species": ["cat"]},
    # 犬型专属
    "loyal_guard":   {"name": "忠诚守护", "type": "战斗辅助", "cost": 2, "desc": "被攻击时有30%概率反击",    "effect": {"counter": 0.3}, "species": ["dog"]},
    "nose_track":    {"name": "追踪",     "type": "探险",   "cost": 2, "desc": "迷宫地图可见范围+1格",       "effect": {"view_range": 1}, "species": ["dog"]},
    # 鸟型专属
    "sky_view":      {"name": "鸟瞰",     "type": "探险",   "cost": 3, "desc": "可看到迷宫整层地图",         "effect": {"full_map": True}, "species": ["bird"]},
    "melody":        {"name": "悦耳旋律", "type": "安抚",   "cost": 1, "desc": "玩耍时快乐恢复+15",         "effect": {"play_happiness": 15}, "species": ["bird"]},
    # 机械型专属
    "overclock":     {"name": "超频",     "type": "战斗辅助", "cost": 3, "desc": "战斗胜率+25%",             "effect": {"battle_win": 0.25}, "species": ["mech"]},
    "self_repair":   {"name": "自我修复", "type": "治愈",   "cost": 2, "desc": "每小时自动恢复5点健康",      "effect": {"auto_heal": 5}, "species": ["mech"]},
    # 神秘型专属
    "void_step":     {"name": "虚空步",   "type": "探险",   "cost": 3, "desc": "每次探险开始时随机传送",     "effect": {"teleport": True}, "species": ["mystery"]},
    "ancient_pulse": {"name": "古老脉动", "type": "被动",   "cost": 4, "desc": "所有属性衰减速度-20%",       "effect": {"decay_reduction": 0.2}, "species": ["mystery"]},
}


class Skill(Base):
    """宠物已学技能"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    skill_key = Column(String(64), nullable=False)
    level = Column(Integer, default=1)   # 技能等级（最高5）
    is_active = Column(Boolean, default=True)   # 主动技能是否装备

    pet = relationship("Pet", back_populates="skills")

    @property
    def definition(self) -> dict:
        return SKILL_DEFINITIONS.get(self.skill_key, {})

    @property
    def name(self) -> str:
        return self.definition.get("name", self.skill_key)

    def __repr__(self) -> str:
        return f"<Skill {self.skill_key} lv{self.level} pet={self.pet_id}>"
