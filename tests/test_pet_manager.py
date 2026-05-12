"""PetManager 测试"""
import pytest
from datetime import datetime, timezone, timedelta

from termipet.core.pet_manager import PetManager


class TestAdopt:
    """测试领养功能"""

    def test_adopt_basic(self, db_session):
        """领养基本流程"""
        pm = PetManager(db_session)
        pet = pm.adopt(species_key="cat", name="小橘")

        assert pet is not None
        assert pet.name == "小橘"
        assert pet.species_key == "cat"
        assert pet.stage == "蛋"
        assert pet.is_active is True
        assert pet.coins == 100
        assert pet.stardust == 0
        # 检查家园是否创建
        assert pet.home is not None

    def test_adopt_invalid_species(self, db_session):
        """领养无效物种"""
        pm = PetManager(db_session)
        with pytest.raises(ValueError) as exc_info:
            pm.adopt(species_key="invalid_species", name="测试")
        assert "未知物种" in str(exc_info.value)

    def test_adopt_empty_name(self, db_session):
        """空名字"""
        pm = PetManager(db_session)
        with pytest.raises(ValueError) as exc_info:
            pm.adopt(species_key="cat", name="")
        assert "名字不能为空" in str(exc_info.value)

    def test_adopt_whitespace_name(self, db_session):
        """仅空白字符的名字"""
        pm = PetManager(db_session)
        with pytest.raises(ValueError) as exc_info:
            pm.adopt(species_key="cat", name="   ")
        assert "名字不能为空" in str(exc_info.value)

    def test_adopt_all_species(self, db_session):
        """领养所有物种"""
        pm = PetManager(db_session)
        for species_key in ["cat", "dog", "bird", "mech", "mystery"]:
            pet = pm.adopt(species_key=species_key, name=f"测试{species_key}")
            assert pet.species_key == species_key
            # 设为非活跃以便领养下一个
            pet.is_active = False
            db_session.commit()

    def test_adopt_replaces_existing(self, db_session):
        """领养新宠物替换现有的活跃状态"""
        pm = PetManager(db_session)
        pet1 = pm.adopt(species_key="cat", name="第一只")
        assert pet1.is_active is True

        pet2 = pm.adopt(species_key="dog", name="第二只")
        assert pet2.is_active is True
        db_session.refresh(pet1)
        assert pet1.is_active is False


class TestApplyDecay:
    """测试属性衰减"""

    def test_apply_decay_no_time(self, db_session, sample_pet):
        """时间间隔极短时无衰减"""
        pm = PetManager(db_session)
        initial_hunger = sample_pet.hunger

        deltas = pm.apply_decay(sample_pet)
        assert deltas == {}

        assert sample_pet.hunger == initial_hunger

    def test_apply_decay_with_time(self, db_session, sample_pet):
        """时间间隔后有衰减"""
        pm = PetManager(db_session)

        # 将 last_updated 设为1小时前
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        initial_hunger = sample_pet.hunger
        deltas = pm.apply_decay(sample_pet)

        assert "hunger" in deltas
        assert deltas["hunger"] < 0
        assert sample_pet.hunger < initial_hunger

    def test_apply_decay_max_offline(self, db_session, sample_pet):
        """离线超过7天只计算7天衰减"""
        pm = PetManager(db_session)

        # 将 last_updated 设为10天前
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(days=10)
        db_session.commit()

        deltas = pm.apply_decay(sample_pet)

        # 验证衰减不会导致负值
        assert sample_pet.hunger >= 0
        assert sample_pet.happiness >= 0
        assert sample_pet.energy >= 0
        assert sample_pet.cleanliness >= 0


class TestFeed:
    """测试喂食功能"""

    def test_feed_normal(self, db_session, sample_pet):
        """普通喂食"""
        pm = PetManager(db_session)
        initial_hunger = sample_pet.hunger

        result = pm.feed(sample_pet)

        assert result["item"] == "普通饲料"
        assert "饱腹" in result["effects"]
        assert sample_pet.hunger > initial_hunger
        assert sample_pet.last_fed is not None

    def test_feed_raises_when_no_item(self, db_session, sample_pet):
        """使用不存在的物品喂食"""
        pm = PetManager(db_session)
        with pytest.raises(ValueError) as exc_info:
            pm.feed(sample_pet, item_key="nonexistent_item")
        assert "背包中" in str(exc_info.value)


class TestPlay:
    """测试玩耍功能"""

    def test_play_normal(self, db_session, sample_pet):
        """正常玩耍"""
        pm = PetManager(db_session)
        initial_happiness = sample_pet.happiness
        initial_energy = sample_pet.energy

        result = pm.play(sample_pet)

        assert "happiness_gain" in result
        assert result["happiness_gain"] > 0
        assert sample_pet.happiness > initial_happiness
        assert sample_pet.energy < initial_energy
        assert sample_pet.last_played is not None

    def test_play_low_energy(self, db_session, sample_pet):
        """精力不足时玩耍"""
        pm = PetManager(db_session)
        sample_pet.energy = 5.0
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            pm.play(sample_pet)
        assert "太累了" in str(exc_info.value)
        assert "精力" in str(exc_info.value)


class TestClean:
    """测试清洁功能"""

    def test_clean_normal(self, db_session, sample_pet):
        """正常清洁"""
        pm = PetManager(db_session)
        initial_cleanliness = sample_pet.cleanliness

        result = pm.clean(sample_pet)

        assert "cleanliness_gain" in result
        assert sample_pet.cleanliness > initial_cleanliness
        assert sample_pet.last_cleaned is not None


class TestSleep:
    """测试睡眠功能"""

    def test_sleep_normal(self, db_session, sample_pet):
        """正常睡觉"""
        pm = PetManager(db_session)
        initial_energy = sample_pet.energy

        result = pm.sleep(sample_pet, hours=4.0)

        assert result["hours"] == 4.0
        assert result["energy_gain"] > 0
        assert sample_pet.energy > initial_energy
        assert sample_pet.last_slept is not None

    def test_sleep_range_boundaries(self, db_session, sample_pet):
        """睡眠时间边界值"""
        pm = PetManager(db_session)

        # 测试最小值
        result = pm.sleep(sample_pet, hours=0.1)
        assert result["hours"] == 0.5  # 最小为0.5

        # 测试最大值
        result = pm.sleep(sample_pet, hours=24.0)
        assert result["hours"] == 12.0  # 最大为12


class TestCoins:
    """测试金币操作"""

    def test_add_coins(self, db_session, sample_pet):
        """添加金币"""
        pm = PetManager(db_session)
        initial = sample_pet.coins

        pm.add_coins(sample_pet, 100)

        assert sample_pet.coins == initial + 100

    def test_spend_coins_normal(self, db_session, sample_pet):
        """正常消费金币"""
        pm = PetManager(db_session)
        initial = sample_pet.coins

        pm.spend_coins(sample_pet, 50)

        assert sample_pet.coins == initial - 50

    def test_spend_coins_fail(self, db_session, sample_pet):
        """金币不足"""
        pm = PetManager(db_session)
        initial = sample_pet.coins

        with pytest.raises(ValueError) as exc_info:
            pm.spend_coins(sample_pet, initial + 100)
        assert "金币不足" in str(exc_info.value)

        # 确认金币未变化
        assert sample_pet.coins == initial


class TestStardust:
    """测试星尘操作"""

    def test_add_stardust(self, db_session, sample_pet):
        """添加星尘"""
        pm = PetManager(db_session)
        initial = sample_pet.stardust

        pm.add_stardust(sample_pet, 10)

        assert sample_pet.stardust == initial + 10

    def test_spend_stardust_fail(self, db_session, sample_pet):
        """星尘不足"""
        pm = PetManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            pm.spend_stardust(sample_pet, 1000)
        assert "星尘不足" in str(exc_info.value)


class TestGetActivePet:
    """测试获取活跃宠物"""

    def test_get_active_pet(self, db_session, sample_pet):
        """获取活跃宠物"""
        pm = PetManager(db_session)
        pet = pm.get_active_pet()
        assert pet is not None
        assert pet.is_active is True

    def test_require_active_pet_raises(self, db_session):
        """没有宠物时抛出异常"""
        pm = PetManager(db_session)
        with pytest.raises(ValueError) as exc_info:
            pm.require_active_pet()
        assert "还没有宠物" in str(exc_info.value)
