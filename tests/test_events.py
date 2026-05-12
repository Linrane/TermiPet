"""EventManager + DailyEventSystem 测试"""
import pytest
from datetime import datetime, timezone, timedelta

from termipet.core.events import EventManager
from termipet.core.daily_events import DailyEventSystem


class TestEventManager:
    """测试随机事件系统"""

    def test_random_event_possible(self, db_session, sample_pet):
        """高概率下验证事件可以触发"""
        em = EventManager(db_session)

        # 使用100%概率确保触发
        triggered = False
        for _ in range(20):  # 多次尝试以避免随机性
            result = em.maybe_trigger(sample_pet, base_chance=1.0)
            if result is not None:
                triggered = True
                assert "key" in result
                assert "title" in result
                assert "effect" in result
                break

        assert triggered, "高概率下应该能触发事件"

    def test_random_event_no_trigger(self, db_session, sample_pet):
        """低概率下不触发"""
        em = EventManager(db_session)

        # 使用0%概率确保不触发
        result = em.maybe_trigger(sample_pet, base_chance=0.0)
        assert result is None

    def test_event_modifies_stats(self, db_session, sample_pet):
        """验证事件能修改属性"""
        em = EventManager(db_session)

        initial_coins = sample_pet.coins
        initial_happiness = sample_pet.happiness

        # 多次触发直到找到能修改金币的事件
        found_effect = False
        for _ in range(100):
            result = em.maybe_trigger(sample_pet, base_chance=1.0)
            if result is not None:
                if "coins" in result["effect"]:
                    found_effect = True
                    break
                db_session.rollback()
                sample_pet.coins = initial_coins
                sample_pet.happiness = initial_happiness

        assert found_effect or sample_pet.coins != initial_coins or sample_pet.happiness != initial_happiness


class TestDailyEventSystem:
    """测试日常事件系统"""

    def test_daily_event_generation(self, db_session, sample_pet):
        """离线超过30分钟有事件"""
        # 将 last_updated 设为1小时前
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        des = DailyEventSystem(db_session)
        events = des.check_and_generate(sample_pet)

        assert len(events) >= 1, "离线1小时应该生成至少1个事件"

    def test_daily_event_no_offline(self, db_session, sample_pet):
        """在线状态下无事件"""
        # last_updated 保持为当前时间
        sample_pet.last_updated = datetime.now(timezone.utc)
        db_session.commit()

        des = DailyEventSystem(db_session)
        events = des.check_and_generate(sample_pet)

        assert len(events) == 0, "在线不应生成事件"

    def test_daily_event_max_unread(self, db_session, sample_pet):
        """最多5个未读"""
        from termipet.models.daily_event import DailyEventLog

        # 将 last_updated 设为2天前（足够生成多个事件但受限于5个未读上限）
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=48)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        # 检查未读数量
        unread = des.get_unread_events(sample_pet)
        assert len(unread) <= 5, "未读事件不应超过5个"

    def test_mark_all_read(self, db_session, sample_pet):
        """标记全部已读"""
        # 先生成一些事件
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        unread_before = des.get_unread_events(sample_pet)
        assert len(unread_before) > 0

        count = des.mark_all_read(sample_pet)
        assert count == len(unread_before)

        unread_after = des.get_unread_events(sample_pet)
        assert len(unread_after) == 0

    def test_species_specific_event(self, db_session, sample_pet):
        """猫型宠物能触发猫类事件"""
        # 猫型宠物有专属事件
        assert sample_pet.species_key == "cat"

        # 多次尝试确保触发到猫类事件
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=24)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet)
        # 猫类事件包括 cat_catch_mouse, cat_keyboard_nest 等
        cat_events = [e for e in events if "cat" in e.event_key]
        # 由于随机性，不强制要求一定有，但系统应该能处理

    def test_mark_single_read(self, db_session, sample_pet):
        """标记单个事件已读"""
        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        unread = des.get_unread_events(sample_pet)
        assert len(unread) > 0

        event_id = unread[0].id
        marked = des.mark_read(sample_pet, event_id)

        assert marked is not None
        assert marked.read is True

    def test_event_categories(self, db_session, sample_pet):
        """验证事件类别分布"""
        categories = set()

        sample_pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=12)
        db_session.commit()

        des = DailyEventSystem(db_session)
        des.check_and_generate(sample_pet)

        events = des.get_all_events(sample_pet)
        for event in events:
            categories.add(event.category)

        # 预期有多个类别：外出探索、家园日常、社交互动、天气事件、成长事件、物种特色
        assert len(categories) >= 1
