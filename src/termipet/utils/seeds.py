"""游戏数据种子初始化 — 物种、物品、技能配置"""
from __future__ import annotations

import json
from sqlalchemy.orm import Session

from termipet.database import get_session, init_db
from termipet.models.pet import Species
from termipet.models.item import Item


# ── 物种数据 ──────────────────────────────────────────────────────────────────
SPECIES_DATA = [
    {
        "key": "cat", "name_zh": "猫型灵兽",
        "description": "来自数据裂隙的影子层，灵敏神秘，擅长躲避陷阱",
        "ascii_art_key": "cat",
        "init_hunger": 65.0, "init_happiness": 75.0, "init_cleanliness": 85.0,
        "init_health": 80.0, "init_energy": 75.0, "init_intelligence": 65.0,
        "init_bond": 20.0, "init_constitution": 60.0,
        "hunger_decay": 1.1, "happiness_decay": 0.9, "cleanliness_decay": 0.7, "energy_decay": 1.0,
        "skill_tree_json": json.dumps(["quick_heal", "treasure_nose", "shadow_step", "purr_therapy", "night_hunter", "lucky_star"]),
        "talent_pool_json": json.dumps(["大胃王", "探险家", "夜猫子", "甜睡者"]),
    },
    {
        "key": "dog", "name_zh": "犬型灵兽",
        "description": "忠诚勇敢，战斗能力强，善于追踪",
        "ascii_art_key": "dog",
        "init_hunger": 70.0, "init_happiness": 70.0, "init_cleanliness": 70.0,
        "init_health": 90.0, "init_energy": 80.0, "init_intelligence": 55.0,
        "init_bond": 30.0, "init_constitution": 80.0,
        "hunger_decay": 1.2, "happiness_decay": 1.1, "cleanliness_decay": 1.0, "energy_decay": 1.1,
        "skill_tree_json": json.dumps(["quick_heal", "loyal_guard", "nose_track", "battle_stance", "tough_skin", "comfort_song"]),
        "talent_pool_json": json.dumps(["大胃王", "铁胃", "自愈力", "社交达人"]),
    },
    {
        "key": "bird", "name_zh": "鸟型灵兽",
        "description": "飞翔于数据流之上，视野开阔，能鸟瞰整个迷宫",
        "ascii_art_key": "bird",
        "init_hunger": 60.0, "init_happiness": 80.0, "init_cleanliness": 80.0,
        "init_health": 70.0, "init_energy": 90.0, "init_intelligence": 70.0,
        "init_bond": 25.0, "init_constitution": 55.0,
        "hunger_decay": 0.9, "happiness_decay": 0.8, "cleanliness_decay": 0.8, "energy_decay": 1.2,
        "skill_tree_json": json.dumps(["sky_view", "melody", "sharp_mind", "forager", "night_hunter", "lucky_star"]),
        "talent_pool_json": json.dumps(["探险家", "天才儿童", "甜睡者", "夜猫子"]),
    },
    {
        "key": "mech", "name_zh": "机械型灵兽",
        "description": "古老程序的残影，用钢铁外壳包裹柔软的内核",
        "ascii_art_key": "mech",
        "init_hunger": 50.0, "init_happiness": 60.0, "init_cleanliness": 90.0,
        "init_health": 100.0, "init_energy": 85.0, "init_intelligence": 80.0,
        "init_bond": 10.0, "init_constitution": 100.0,
        "hunger_decay": 0.6, "happiness_decay": 1.3, "cleanliness_decay": 0.3, "energy_decay": 0.8,
        "skill_tree_json": json.dumps(["overclock", "self_repair", "battle_stance", "tough_skin", "sharp_mind", "lucky_star"]),
        "talent_pool_json": json.dumps(["铁胃", "自愈力", "天才儿童", "探险家"]),
    },
    {
        "key": "mystery", "name_zh": "神秘型灵兽",
        "description": "来历不明的存在，拥有异常强大的古老力量",
        "ascii_art_key": "mystery",
        "init_hunger": 55.0, "init_happiness": 65.0, "init_cleanliness": 75.0,
        "init_health": 75.0, "init_energy": 70.0, "init_intelligence": 95.0,
        "init_bond": 15.0, "init_constitution": 65.0,
        "hunger_decay": 0.8, "happiness_decay": 1.0, "cleanliness_decay": 0.6, "energy_decay": 0.9,
        "skill_tree_json": json.dumps(["void_step", "ancient_pulse", "quick_heal", "treasure_nose", "lucky_star", "sharp_mind"]),
        "talent_pool_json": json.dumps(["夜猫子", "天才儿童", "社交达人", "探险家"]),
    },
]


# ── 物品数据 ──────────────────────────────────────────────────────────────────
ITEMS_DATA = [
    # 食物/消耗品
    {"key": "basic_food",       "name": "基础饲料",     "item_type": "consumable", "rarity": "普通",   "effects_json": json.dumps({"hunger": 30, "health": 5}),       "buy_price": 10,  "sell_price": 3,  "in_shop": True},
    {"key": "premium_grain",    "name": "高级粮食",     "item_type": "consumable", "rarity": "稀有",   "effects_json": json.dumps({"hunger": 50, "health": 10}),      "buy_price": 25,  "sell_price": 10, "in_shop": True},
    {"key": "grilled_fish_item","name": "烤鱼",         "item_type": "consumable", "rarity": "普通",   "effects_json": json.dumps({"hunger": 40, "happiness": 10}),   "buy_price": 20,  "sell_price": 8,  "in_shop": False},
    {"key": "energy_potion_item","name": "精力药剂",    "item_type": "consumable", "rarity": "稀有",   "effects_json": json.dumps({"energy": 40}),                    "buy_price": 30,  "sell_price": 12, "in_shop": False},
    {"key": "super_food_item",  "name": "超级饲料",     "item_type": "consumable", "rarity": "传说",   "effects_json": json.dumps({"hunger": 80, "health": 20, "happiness": 20}), "buy_price": 80, "sell_price": 30, "in_shop": False},
    {"key": "health_potion",    "name": "治愈药水",     "item_type": "consumable", "rarity": "普通",   "effects_json": json.dumps({"health": 30}),                    "buy_price": 20,  "sell_price": 8,  "in_shop": True},
    {"key": "rare_treat",       "name": "稀有零食",     "item_type": "consumable", "rarity": "稀有",   "effects_json": json.dumps({"happiness": 30, "bond": 5}),       "buy_price": 35,  "sell_price": 15, "in_shop": True},
    {"key": "skill_book_basic_item","name": "基础技能书","item_type":"consumable","rarity": "稀有",   "effects_json": json.dumps({"skill_points": 2}),               "buy_price": 60,  "sell_price": 25, "in_shop": False},

    # 材料
    {"key": "raw_fish",         "name": "生鱼",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 8,  "sell_price": 3,  "in_shop": True},
    {"key": "seasoning",        "name": "调味料",       "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 5,  "sell_price": 2,  "in_shop": True},
    {"key": "herb",             "name": "草药",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 8,  "sell_price": 3,  "in_shop": True},
    {"key": "water",            "name": "清水",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 3,  "sell_price": 1,  "in_shop": True},
    {"key": "iron_ingot",       "name": "铁锭",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 15, "sell_price": 6,  "in_shop": True},
    {"key": "leather",          "name": "皮革",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 12, "sell_price": 5,  "in_shop": True},
    {"key": "paper",            "name": "纸张",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 4,  "sell_price": 1,  "in_shop": True},
    {"key": "ink",              "name": "墨水",         "item_type": "material",   "rarity": "普通",   "effects_json": json.dumps({}), "buy_price": 6,  "sell_price": 2,  "in_shop": True},
    {"key": "data_shard",       "name": "数据碎片",     "item_type": "material",   "rarity": "稀有",   "effects_json": json.dumps({}), "buy_price": 20, "sell_price": 10, "in_shop": True},
    {"key": "wind_crystal",     "name": "风晶石",       "item_type": "material",   "rarity": "稀有",   "effects_json": json.dumps({}), "buy_price": 35, "sell_price": 15, "in_shop": False},
    {"key": "star_metal",       "name": "星辰金属",     "item_type": "material",   "rarity": "传说",   "effects_json": json.dumps({}), "buy_price": 80, "sell_price": 35, "in_shop": False},
    {"key": "magic_crystal",    "name": "魔法水晶",     "item_type": "material",   "rarity": "传说",   "effects_json": json.dumps({}), "buy_price": 60, "sell_price": 25, "in_shop": False},
    {"key": "magic_powder",     "name": "魔法粉末",     "item_type": "material",   "rarity": "稀有",   "effects_json": json.dumps({}), "buy_price": 25, "sell_price": 10, "in_shop": True},

    # 装备
    {"key": "data_collar_item", "name": "数据项圈",     "item_type": "equipment",  "rarity": "稀有",
     "effects_json": json.dumps({"intelligence": 10}), "buy_price": 80, "sell_price": 30, "in_shop": True, "equip_slot": "neck"},
    {"key": "speed_boots_item", "name": "疾风靴",       "item_type": "equipment",  "rarity": "稀有",
     "effects_json": json.dumps({"energy": 15}),        "buy_price": 70, "sell_price": 25, "in_shop": True, "equip_slot": "feet"},
    {"key": "star_armor_item",  "name": "星辰甲",       "item_type": "equipment",  "rarity": "传说",
     "effects_json": json.dumps({"health": 20, "constitution": 15}), "buy_price": 200, "sell_price": 80, "in_shop": False, "equip_slot": "body"},
    {"key": "lucky_charm",      "name": "幸运符",       "item_type": "equipment",  "rarity": "稀有",
     "effects_json": json.dumps({"happiness": 10}),     "buy_price": 60, "sell_price": 20, "in_shop": True, "equip_slot": "neck"},

    # 收藏品
    {"key": "ancient_coin",     "name": "古代金币",     "item_type": "collectible","rarity": "传说",
     "effects_json": json.dumps({}), "buy_price": 0, "sell_price": 50, "in_shop": False},
    {"key": "crystal_egg",      "name": "水晶蛋",       "item_type": "collectible","rarity": "传说",
     "effects_json": json.dumps({}), "buy_price": 0, "sell_price": 100, "in_shop": False},
]


def seed_data(session: Session) -> None:
    """向数据库写入初始游戏数据（已存在则跳过）"""
    # 物种
    for data in SPECIES_DATA:
        if not session.query(Species).filter_by(key=data["key"]).first():
            species = Species(**{k: v for k, v in data.items()})
            session.add(species)

    # 物品
    for data in ITEMS_DATA:
        if not session.query(Item).filter_by(key=data["key"]).first():
            item = Item(**{k: v for k, v in data.items()})
            session.add(item)

    session.commit()


def initialize_game() -> None:
    """完整初始化：建表 + 写入种子数据"""
    init_db()
    session = get_session()
    try:
        seed_data(session)
    finally:
        session.close()
