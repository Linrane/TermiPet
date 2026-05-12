"""制作系统 — 配方、材料、合成"""
from __future__ import annotations

from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.home import Home
from termipet.models.item import Item, Inventory
from termipet.core.pet_manager import PetManager


# ── 配方定义 ──────────────────────────────────────────────────────────────────
# key: {name, room, room_level_required, materials: {item_key: qty}, output_item_key, output_qty}
RECIPES: dict[str, dict] = {
    # 厨房食物
    "grilled_fish": {
        "name": "烤鱼",
        "room": "kitchen_level", "room_min": 1,
        "materials": {"raw_fish": 1, "seasoning": 1},
        "output": "grilled_fish_item", "qty": 1,
    },
    "energy_potion": {
        "name": "精力药剂",
        "room": "kitchen_level", "room_min": 2,
        "materials": {"herb": 2, "water": 1},
        "output": "energy_potion_item", "qty": 2,
    },
    "super_food": {
        "name": "超级饲料",
        "room": "kitchen_level", "room_min": 3,
        "materials": {"premium_grain": 3, "magic_powder": 1},
        "output": "super_food_item", "qty": 3,
    },
    # 工坊装备
    "data_collar": {
        "name": "数据项圈",
        "room": "workshop_level", "room_min": 1,
        "materials": {"iron_ingot": 2, "data_shard": 1},
        "output": "data_collar_item", "qty": 1,
    },
    "speed_boots": {
        "name": "疾风靴",
        "room": "workshop_level", "room_min": 2,
        "materials": {"leather": 2, "wind_crystal": 1},
        "output": "speed_boots_item", "qty": 1,
    },
    "star_armor": {
        "name": "星辰甲",
        "room": "workshop_level", "room_min": 3,
        "materials": {"star_metal": 3, "magic_crystal": 2},
        "output": "star_armor_item", "qty": 1,
    },
    # 图书室技能书
    "skill_book_basic": {
        "name": "基础技能书",
        "room": "library_level", "room_min": 1,
        "materials": {"paper": 5, "ink": 2},
        "output": "skill_book_basic_item", "qty": 1,
    },
}


class CraftingManager:
    def __init__(self, session: Session):
        self.session = session
        self.pm = PetManager(session)

    def list_available_recipes(self, pet: Pet) -> list[dict]:
        """列出当前可制作的配方"""
        home = self.session.query(Home).filter_by(pet_id=pet.id).first()
        if home is None:
            return []

        available = []
        for key, recipe in RECIPES.items():
            room_val = getattr(home, recipe["room"], 0)
            if room_val < recipe["room_min"]:
                continue
            # 检查材料
            can_craft, missing = self._check_materials(pet, recipe["materials"])
            available.append({
                "key": key,
                "name": recipe["name"],
                "materials": recipe["materials"],
                "output": recipe["output"],
                "qty": recipe["qty"],
                "can_craft": can_craft,
                "missing": missing,
            })
        return available

    def craft(self, pet: Pet, recipe_key: str) -> dict:
        """执行制作"""
        recipe_key = recipe_key.lower().strip()
        recipe = RECIPES.get(recipe_key)

        # 支持名字匹配
        if recipe is None:
            for k, r in RECIPES.items():
                if r["name"] == recipe_key or recipe_key in r["name"]:
                    recipe_key = k
                    recipe = r
                    break

        if recipe is None:
            names = [r["name"] for r in RECIPES.values()]
            raise ValueError(f"未知配方 '{recipe_key}'。\n可用配方：{', '.join(names)}")

        home = self.session.query(Home).filter_by(pet_id=pet.id).first()
        if home is None:
            raise ValueError("家园数据异常，请重新初始化。")

        room_val = getattr(home, recipe["room"], 0)
        if room_val < recipe["room_min"]:
            room_names = {"kitchen_level": "厨房", "workshop_level": "工坊", "library_level": "图书室"}
            room_name = room_names.get(recipe["room"], recipe["room"])
            raise ValueError(
                f"需要 {room_name} 等级 {recipe['room_min']}，当前等级 {room_val}。\n"
                f"使用 [bold]pet home upgrade {room_name}[/] 升级房间。"
            )

        can_craft, missing = self._check_materials(pet, recipe["materials"])
        if not can_craft:
            missing_str = ", ".join(f"{k}×{v}" for k, v in missing.items())
            raise ValueError(f"材料不足！缺少：{missing_str}")

        # 消耗材料
        self._consume_materials(pet, recipe["materials"])

        # 产出物品
        output_item = self.session.query(Item).filter_by(key=recipe["output"]).first()
        if output_item is None:
            raise ValueError(f"配方数据错误：输出物品 '{recipe['output']}' 不存在。")

        inv = self.session.query(Inventory).filter_by(pet_id=pet.id, item_id=output_item.id).first()
        if inv:
            inv.quantity += recipe["qty"]
        else:
            inv = Inventory(pet_id=pet.id, item_id=output_item.id, quantity=recipe["qty"])
            self.session.add(inv)

        self.session.commit()

        from termipet.core.quests import QuestManager
        qm = QuestManager(self.session)
        qm.update_progress(pet, "weekly_craft", 1)

        return {
            "recipe": recipe["name"],
            "output": output_item.name,
            "qty": recipe["qty"],
        }

    def _check_materials(self, pet: Pet, materials: dict[str, int]) -> tuple[bool, dict]:
        missing = {}
        for item_key, required in materials.items():
            inv = (
                self.session.query(Inventory)
                .join(Item)
                .filter(Inventory.pet_id == pet.id, Item.key == item_key)
                .first()
            )
            have = inv.quantity if inv else 0
            if have < required:
                missing[item_key] = required - have
        return len(missing) == 0, missing

    def _consume_materials(self, pet: Pet, materials: dict[str, int]) -> None:
        for item_key, qty in materials.items():
            inv = (
                self.session.query(Inventory)
                .join(Item)
                .filter(Inventory.pet_id == pet.id, Item.key == item_key)
                .first()
            )
            if inv:
                inv.quantity -= qty
                if inv.quantity <= 0:
                    self.session.delete(inv)
