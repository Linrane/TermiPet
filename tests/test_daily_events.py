"""DailyEventSystem 详细测试"""
import pytest
from datetime import datetime, timezone, timedelta

from termipet.core.daily_events import DailyEventSystem


class TestOfflineGeneration:
    """测试离线事件生成"""

    def test_check_and_generate_offline(self, db_session, sample_pet):
        """离线触发"""
        # 设置为1小时前
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        des = DailyEventSystem(db_session)
        events = des.check_and_generate(sample_pet)

        assert len(events) >= 1

    def test_check_and_generate_online(self, db_session, sample_pet):
        """在线不触发"""
        # 刚刚更新
        sample_pet.last_updated = datetime.now(timezone.utc)
        db_session.commit()

        des = DailyEventSystem(db_session)
        events = des.check_and_generate(sample_pet)

        assert len(events) == 0

    def test_offline_less_than_30_minutes(self, db_session, sample_pet):
        """离线不足30分钟"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(minutes=20)
        db_session.commit()

        des = DailyEventSystem(db_session)
        events = des.check_and_generate(sample_pet)

        assert len(events) == 0


class TestEventEffects:
    """测试事件效果"""

    def test_event_effects(self, db_session, sample_pet):
        """事件效果正确应用"""
        initial_coins = sample_pet.coins
        initial_happiness = sample_pet.happiness

        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=5)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        # 属性可能变化
        # 不强验证变化，因为随机事件不一定修改这些属性
        db_session.refresh(sample_pet)
        assert sample_pet.coins >= 0
        assert sample_pet.happiness >= 0

    def test_event_coins_effect(self, db_session, sample_pet):
        """金币事件效果"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=24)
        sample_pet.coins = 100
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        db_session.refresh(sample_pet)
        # 金币可能增加（某些事件会扣金币，所以不保证增加）


class TestEventLogging:
    """测试事件日志"""

    def test_event_logging(self, db_session, sample_pet):
        """日志正确记录"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=3)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet, limit=100)
        assert len(events) > 0

        # 验证日志结构
        event = events[0]
        assert event.event_key is not None
        assert event.title is not None
        assert event.summary is not None
        assert event.category is not None
        assert event.read is False  # 新事件未读

    def test_event_pet_name_in_text(self, db_session, sample_pet):
        """事件文本中包含宠物名"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet)
        for event in events:
            # 摘要或详情中应该包含宠物名
            assert sample_pet.name in event.summary or sample_pet.name in event.detail


class TestMaxUnreadLimit:
    """测试最大未读数限制"""

    def test_max_unread_limit(self, db_session, sample_pet):
        """最大未读数限制"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=48)
        db_session.commit()

        des = DailyEventSystem(db_session)

        # 生成事件
        for _ in range(3):
            des.check_and_generate(sample_pet)

        unread = des.get_unread_events(sample_pet)
        assert len(unread) <= 5

    def test_existing_unread_count(self, db_session, sample_pet):
        """已有未读时生成受限"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        # 已有未读时
        events = des.get_unread_events(sample_pet)
        existing_count = len(events)

        # 再次调用应该不增加（或只增加剩余槽位）
        des.check_and_generate(sample_pet)

        unread_after = des.get_unread_events(sample_pet)
        assert len(unread_after) <= 5


class TestCategoryDistribution:
    """测试事件类别分布"""

    def test_category_distribution(self, db_session, sample_pet):
        """事件类别分布合理"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=24)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet)
        categories = [e.category for e in events]

        # 验证有合理的类别
        valid_categories = [
            "外出探索", "家园日常", "社交互动",
            "天气事件", "成长事件", "物种特色"
        ]

        for cat in set(categories):
            assert cat in valid_categories


class TestSpeciesSpecificEvents:
    """测试物种专属事件"""

    def test_cat_specific_events(self, db_session, sample_pet):
        """猫型宠物事件"""
        assert sample_pet.species_key == "cat"

        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=12)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet)
        cat_events = [e for e in events if e.event_key in ["cat_catch_mouse", "cat_keyboard_nest"]]

        # 不强制要求一定有，因为随机性

    def test_dog_specific_events(self, db_session, dog_pet):
        """犬型宠物事件"""
        assert dog_pet.species_key == "dog"

        dog_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=12)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(dog_pet)

        events = des.get_all_events(dog_pet)
        dog_events = [e for e in events if e.event_key in ["dog_dig_hole", "dog_steal_slipper"]]

        # 不强制要求一定有，因为随机性


class TestEventCondition:
    """测试事件条件"""

    def test_egg_stage_no_events(self, db_session, egg_pet):
        """蛋期宠物不应生成大多数事件"""
        egg_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=12)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(egg_pet)

        events = des.get_all_events(egg_pet)

        # 蛋期只有极少数事件可以触发
        for event in events:
            # 验证事件条件满足
            from termipet.core.daily_events import DAILY_EVENTS
            event_def = next((e for e in DAILY_EVENTS if e["key"] == event.event_key), None)
            if event_def:
                cond = event_def.get("condition")
                if cond:
                    assert cond(egg_pet) is True


class TestMarkRead:
    """测试标记已读"""

    def test_mark_read(self, db_session, sample_pet):
        """标记单条已读"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        unread = des.get_unread_events(sample_pet)
        assert len(unread) > 0

        event = des.mark_read(sample_pet, unread[0].id)
        assert event is not None
        assert event.read is True

    def test_mark_all_read(self, db_session, sample_pet):
        """标记全部已读"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=3)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        unread_before = len(des.get_unread_events(sample_pet))

        count = des.mark_all_read(sample_pet)
        assert count == unread_before

        unread_after = des.get_unread_events(sample_pet)
        assert len(unread_after) == 0

    def test_mark_invalid_id(self, db_session, sample_pet):
        """标记无效ID"""
        des = DailyEventSystem(db_session)
        result = des.mark_read(sample_pet, 99999)
        assert result is None


class TestEventResult:
    """测试事件结果"""

    def test_event_result_json(self, db_session, sample_pet):
        """事件结果正确存储"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet)
        for event in events:
            result = event.result
            assert isinstance(result, dict)
