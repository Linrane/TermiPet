"""经济系统 — 商店买卖、材料交易"""
from __future__ import annotations

from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.item import Item, Inventory
from termipet.core.pet_manager import PetManager


class EconomyManager:
    def __init__(self, session: Session):
        self.session = session
        self.pm = PetManager(session)

    def list_shop_items(self, category: str | None = None) -> list[Item]:
        q = self.session.query(Item).filter_by(in_shop=True)
        if category:
            CAT_MAP = {
                "食物": "consumable", "food": "consumable",
                "材料": "material",   "mat": "material",
                "装备": "equipment",  "equip": "equipment",
                "收藏": "collectible",
            }
            item_type = CAT_MAP.get(category, category)
            q = q.filter(Item.item_type == item_type)
        return q.order_by(Item.item_type, Item.rarity, Item.name).all()

    def buy(self, pet: Pet, item_key: str, count: int = 1) -> dict:
        """购买物品"""
        count = max(1, min(count, 99))

        # 查找物品（支持 key 或名字模糊匹配）
        item = self.session.query(Item).filter_by(key=item_key, in_shop=True).first()
        if item is None:
            item = self.session.query(Item).filter(
                Item.name.contains(item_key), Item.in_shop == True
            ).first()
        if item is None:
            raise ValueError(f"商店中没有 '{item_key}'，请用 [bold]pet shop list[/] 查看可购买物品。")

        total = item.buy_price * count
        self.pm.spend_coins(pet, total)

        # 添加到背包
        inv = self.session.query(Inventory).filter_by(pet_id=pet.id, item_id=item.id).first()
        if inv:
            inv.quantity += count
        else:
            inv = Inventory(pet_id=pet.id, item_id=item.id, quantity=count)
            self.session.add(inv)

        self.session.commit()
        return {"item": item.name, "count": count, "cost": total, "remaining_coins": pet.coins}

    def sell(self, pet: Pet, item_key: str, count: int = 1) -> dict:
        """出售物品"""
        count = max(1, min(count, 999))

        inv = (
            self.session.query(Inventory)
            .join(Item)
            .filter(Inventory.pet_id == pet.id)
            .filter(Item.key == item_key)
            .first()
        )
        if inv is None:
            inv = (
                self.session.query(Inventory)
                .join(Item)
                .filter(Inventory.pet_id == pet.id)
                .filter(Item.name.contains(item_key))
                .first()
            )
        if inv is None:
            raise ValueError(f"背包中没有 '{item_key}'。")
        if inv.equipped:
            raise ValueError(f"'{inv.item.name}' 正在装备中，请先卸下再出售。")

        actual = min(count, inv.quantity)
        earned = inv.item.sell_price * actual
        pet.coins += earned

        inv.quantity -= actual
        if inv.quantity <= 0:
            self.session.delete(inv)

        self.session.commit()
        return {"item": inv.item.name, "count": actual, "earned": earned, "coins": pet.coins}

    def get_inventory(self, pet: Pet) -> list[Inventory]:
        return (
            self.session.query(Inventory)
            .join(Item)
            .filter(Inventory.pet_id == pet.id)
            .filter(Inventory.quantity > 0)
            .order_by(Item.item_type, Item.rarity)
            .all()
        )

    def equip(self, pet: Pet, item_key: str) -> dict:
        """装备物品"""
        inv = (
            self.session.query(Inventory)
            .join(Item)
            .filter(Inventory.pet_id == pet.id)
            .filter(Item.key == item_key)
            .filter(Item.item_type == "equipment")
            .first()
        )
        if inv is None:
            inv = (
                self.session.query(Inventory)
                .join(Item)
                .filter(Inventory.pet_id == pet.id)
                .filter(Item.name.contains(item_key))
                .filter(Item.item_type == "equipment")
                .first()
            )
        if inv is None:
            raise ValueError(f"背包中没有装备 '{item_key}'。")

        item = inv.item
        slot = item.equip_slot or "body"

        # 卸下同槽位装备
        equipped = pet.equipped_items
        if slot in equipped:
            old_inv = self.session.query(Inventory).filter_by(
                pet_id=pet.id, item_id=equipped[slot], equipped=True
            ).first()
            if old_inv:
                old_inv.equipped = False

        equipped[slot] = item.id
        pet.equipped_items = equipped
        inv.equipped = True

        # 应用装备效果
        for stat, val in item.effects.items():
            self.pm._apply_stat(pet, stat, val)

        self.session.commit()
        return {"item": item.name, "slot": slot}

    def unequip(self, pet: Pet, item_key: str) -> dict:
        """卸下装备"""
        inv = (
            self.session.query(Inventory)
            .join(Item)
            .filter(Inventory.pet_id == pet.id)
            .filter(Inventory.equipped == True)
            .filter(Item.key == item_key)
            .first()
        )
        if inv is None:
            inv = (
                self.session.query(Inventory)
                .join(Item)
                .filter(Inventory.pet_id == pet.id)
                .filter(Inventory.equipped == True)
                .filter(Item.name.contains(item_key))
                .first()
            )
        if inv is None:
            raise ValueError(f"'{item_key}' 未装备或不存在。")

        item = inv.item
        slot = item.equip_slot or "body"
        equipped = pet.equipped_items
        equipped.pop(slot, None)
        pet.equipped_items = equipped
        inv.equipped = False

        # 撤销装备效果
        for stat, val in item.effects.items():
            self.pm._apply_stat(pet, stat, -val)

        self.session.commit()
        return {"item": item.name, "slot": slot}
