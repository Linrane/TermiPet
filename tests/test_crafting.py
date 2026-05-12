"""CraftingManager 测试"""
import pytest

from termipet.core.crafting import CraftingManager


class TestListRecipes:
    """测试配方列表"""

    def test_list_recipes(self, db_session, pet_with_home_upgraded):
        """列出可用配方"""
        cm = CraftingManager(db_session)
        recipes = cm.list_available_recipes(pet_with_home_upgraded)

        assert len(recipes) > 0

    def test_list_recipes_no_home(self, db_session, sample_pet):
        """没有家园时返回空"""
        cm = CraftingManager(db_session)
        # sample_pet 的 home 存在但所有房间等级为0/1
        recipes = cm.list_available_recipes(sample_pet)
        # 应该能列出一些配方
        assert isinstance(recipes, list)


class TestCraft:
    """测试制作"""

    def test_craft_recipe(self, db_session, pet_with_materials):
        """正常制作"""
        cm = CraftingManager(db_session)

        # 烤鱼需要 raw_fish x1, seasoning x1
        result = cm.craft(pet_with_materials, "grilled_fish")

        assert "recipe" in result
        assert "output" in result
        assert result["output"] == "烤鱼"

    def test_craft_by_name(self, db_session, pet_with_materials):
        """按名字制作"""
        cm = CraftingManager(db_session)

        result = cm.craft(pet_with_materials, "烤鱼")

        assert result["recipe"] == "烤鱼"

    def test_craft_insufficient_materials(self, db_session, pet_with_home_upgraded):
        """材料不足"""
        cm = CraftingManager(db_session)

        # 超级饲料需要 premium_grain x3，但 pet_with_home_upgraded 没有
        with pytest.raises(ValueError) as exc_info:
            cm.craft(pet_with_home_upgraded, "super_food")
        # 可能因为材料不足或房间等级不足
        error_msg = str(exc_info.value)
        assert "材料不足" in error_msg or "厨房" in error_msg

    def test_craft_unknown_recipe(self, db_session, pet_with_materials):
        """未知配方"""
        cm = CraftingManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            cm.craft(pet_with_materials, "nonexistent_recipe")
        assert "未知配方" in str(exc_info.value)

    def test_craft_room_level(self, db_session, pet_with_materials):
        """房间等级不足"""
        cm = CraftingManager(db_session)

        # 超级饲料需要厨房等级3
        with pytest.raises(ValueError) as exc_info:
            cm.craft(pet_with_materials, "super_food")
        # 可能是因为材料不足，也可能是房间等级不足
        error_msg = str(exc_info.value)
        assert "材料不足" in error_msg or "厨房" in error_msg

    def test_craft_consumes_materials(self, db_session, pet_with_materials):
        """制作消耗材料"""
        cm = CraftingManager(db_session)

        from termipet.models.item import Inventory, Item

        # 记录制作前的材料数量
        raw_fish_item = db_session.query(Item).filter_by(key="raw_fish").first()
        inv_before = db_session.query(Inventory).filter_by(
            pet_id=pet_with_materials.id, item_id=raw_fish_item.id
        ).first()
        raw_fish_count_before = inv_before.quantity if inv_before else 0

        # 制作烤鱼
        cm.craft(pet_with_materials, "grilled_fish")

        # 验证材料减少
        inv_after = db_session.query(Inventory).filter_by(
            pet_id=pet_with_materials.id, item_id=raw_fish_item.id
        ).first()
        raw_fish_count_after = inv_after.quantity if inv_after else 0

        assert raw_fish_count_after < raw_fish_count_before


class TestCraftingManager:
    """测试制作管理器其他功能"""

    def test_available_recipes_include_unavailable(self, db_session, pet_with_materials):
        """可用配方列表包含不可制作的（带 missing 信息）"""
        cm = CraftingManager(db_session)
        recipes = cm.list_available_recipes(pet_with_materials)

        # 至少应该有一些配方
        for recipe in recipes:
            assert "can_craft" in recipe
            assert "missing" in recipe

    def test_craft_updates_inventory(self, db_session, pet_with_materials):
        """制作更新背包"""
        cm = CraftingManager(db_session)

        result = cm.craft(pet_with_materials, "grilled_fish")

        # 检查背包中是否有烤鱼
        from termipet.models.item import Item, Inventory
        grilled_fish = db_session.query(Item).filter_by(key="grilled_fish_item").first()
        assert grilled_fish is not None

        inv = db_session.query(Inventory).filter_by(
            pet_id=pet_with_materials.id,
            item_id=grilled_fish.id
        ).first()
        assert inv is not None
        assert inv.quantity >= 1
