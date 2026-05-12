"""EconomyManager 测试"""
import pytest

from termipet.core.economy import EconomyManager


class TestListShop:
    """测试商店"""

    def test_list_shop(self, db_session, sample_pet):
        """列出商店物品"""
        em = EconomyManager(db_session)
        items = em.list_shop_items()

        assert len(items) > 0
        for item in items:
            assert item.in_shop is True

    def test_list_shop_by_category(self, db_session, sample_pet):
        """按类别列出商店物品"""
        em = EconomyManager(db_session)

        # 食物类
        food_items = em.list_shop_items(category="食物")
        for item in food_items:
            assert item.item_type == "consumable"

        # 材料类
        mat_items = em.list_shop_items(category="材料")
        for item in mat_items:
            assert item.item_type == "material"

        # 装备类
        equip_items = em.list_shop_items(category="装备")
        for item in equip_items:
            assert item.item_type == "equipment"


class TestBuy:
    """测试购买"""

    def test_buy_item(self, db_session, sample_pet):
        """购买物品"""
        em = EconomyManager(db_session)
        initial_coins = sample_pet.coins

        result = em.buy(sample_pet, "basic_food", count=1)

        assert "item" in result
        assert "cost" in result
        assert sample_pet.coins < initial_coins

    def test_buy_by_name(self, db_session, sample_pet):
        """按名字购买"""
        em = EconomyManager(db_session)
        initial_coins = sample_pet.coins

        result = em.buy(sample_pet, "基础饲料", count=1)

        assert result["item"] == "基础饲料"

    def test_buy_insufficient_coins(self, db_session, sample_pet):
        """金币不足"""
        em = EconomyManager(db_session)
        sample_pet.coins = 5  # 低于大多数物品价格

        with pytest.raises(ValueError) as exc_info:
            em.buy(sample_pet, "basic_food", count=1)
        assert "金币不足" in str(exc_info.value)

    def test_buy_invalid_item(self, db_session, sample_pet):
        """购买不存在的物品"""
        em = EconomyManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            em.buy(sample_pet, "nonexistent_item_xyz", count=1)
        assert "没有" in str(exc_info.value)

    def test_buy_multiple(self, db_session, sample_pet):
        """购买多个"""
        em = EconomyManager(db_session)
        initial_coins = sample_pet.coins

        result = em.buy(sample_pet, "basic_food", count=5)

        assert result["count"] == 5
        assert sample_pet.coins == initial_coins - result["cost"]


class TestSell:
    """测试出售"""

    def test_sell_item(self, db_session, sample_pet):
        """出售物品"""
        # 先购买一些物品
        em = EconomyManager(db_session)
        em.buy(sample_pet, "basic_food", count=3)

        initial_coins = sample_pet.coins

        result = em.sell(sample_pet, "basic_food", count=1)

        assert "earned" in result
        assert sample_pet.coins > initial_coins

    def test_sell_by_name(self, db_session, sample_pet):
        """按名字出售"""
        em = EconomyManager(db_session)
        em.buy(sample_pet, "basic_food", count=2)

        result = em.sell(sample_pet, "基础饲料", count=1)
        assert result["item"] == "基础饲料"

    def test_sell_not_owned(self, db_session, sample_pet):
        """出售不存在的物品"""
        em = EconomyManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            em.sell(sample_pet, "nonexistent_item", count=1)
        assert "背包中" in str(exc_info.value)

    def test_sell_equipped(self, db_session, sample_pet):
        """出售已装备的物品"""
        # 购买并装备
        em = EconomyManager(db_session)
        em.buy(sample_pet, "data_collar_item", count=1)
        em.equip(sample_pet, "data_collar_item")

        with pytest.raises(ValueError) as exc_info:
            em.sell(sample_pet, "data_collar_item", count=1)
        assert "装备中" in str(exc_info.value)


class TestInventory:
    """测试背包"""

    def test_get_inventory_empty(self, db_session, sample_pet):
        """空背包"""
        em = EconomyManager(db_session)
        inv = em.get_inventory(sample_pet)
        assert len(inv) == 0

    def test_get_inventory_with_items(self, db_session, sample_pet):
        """有物品的背包"""
        em = EconomyManager(db_session)
        em.buy(sample_pet, "basic_food", count=3)
        em.buy(sample_pet, "herb", count=2)

        inv = em.get_inventory(sample_pet)
        assert len(inv) >= 2


class TestEquip:
    """测试装备"""

    def test_equip_item(self, db_session, sample_pet):
        """装备物品"""
        em = EconomyManager(db_session)
        em.buy(sample_pet, "data_collar_item", count=1)

        result = em.equip(sample_pet, "data_collar_item")

        assert "item" in result
        assert "slot" in result

    def test_equip_invalid(self, db_session, sample_pet):
        """装备不存在的物品"""
        em = EconomyManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            em.equip(sample_pet, "nonexistent_item")
        assert "背包中没有装备" in str(exc_info.value)

    def test_unequip_item(self, db_session, sample_pet):
        """卸下装备"""
        em = EconomyManager(db_session)
        em.buy(sample_pet, "data_collar_item", count=1)
        em.equip(sample_pet, "data_collar_item")

        result = em.unequip(sample_pet, "data_collar_item")

        assert "item" in result
        assert "slot" in result

    def test_unequip_not_equipped(self, db_session, sample_pet):
        """卸下未装备的物品"""
        em = EconomyManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            em.unequip(sample_pet, "data_collar_item")
        assert "未装备" in str(exc_info.value)
