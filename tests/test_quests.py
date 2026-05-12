"""QuestManager 测试"""
import pytest
from datetime import datetime, timezone, timedelta

from termipet.core.quests import QuestManager


class TestGetQuests:
    """测试获取任务"""

    def test_get_quests(self, db_session, sample_pet):
        """获取任务列表"""
        qm = QuestManager(db_session)
        quests = qm.get_quests(sample_pet)

        assert len(quests) > 0

        # 验证每个任务都有 definition 属性
        for quest in quests:
            assert quest.definition is not None
            assert "name" in quest.definition

    def test_quests_initial_state(self, db_session, sample_pet):
        """任务初始状态"""
        qm = QuestManager(db_session)
        quests = qm.get_quests(sample_pet)

        for quest in quests:
            # 初始时未完成
            assert quest.completed is False
            assert quest.claimed is False


class TestClaimQuest:
    """测试领取任务奖励"""

    def test_claim_completed(self, db_session, sample_pet):
        """领取已完成任务"""
        qm = QuestManager(db_session)

        # 找到一个任务并手动标记为完成
        quests = qm.get_quests(sample_pet)
        quest = quests[0]
        quest.progress = quest.definition.get("target", 1)
        quest.completed = True
        db_session.commit()

        initial_coins = sample_pet.coins
        result = qm.claim_quest(sample_pet, quest.quest_key)

        assert "name" in result
        assert "coins" in result
        assert quest.claimed is True

    def test_claim_not_completed(self, db_session, sample_pet):
        """领取未完成任务"""
        qm = QuestManager(db_session)
        quests = qm.get_quests(sample_pet)
        quest = quests[0]

        with pytest.raises(ValueError) as exc_info:
            qm.claim_quest(sample_pet, quest.quest_key)
        assert "尚未完成" in str(exc_info.value)

    def test_claim_already_claimed(self, db_session, sample_pet):
        """重复领取"""
        qm = QuestManager(db_session)
        quests = qm.get_quests(sample_pet)
        quest = quests[0]

        # 完成并领取
        quest.progress = quest.definition.get("target", 1)
        quest.completed = True
        db_session.commit()
        qm.claim_quest(sample_pet, quest.quest_key)

        # 再次尝试领取
        with pytest.raises(ValueError) as exc_info:
            qm.claim_quest(sample_pet, quest.quest_key)
        assert "已领取" in str(exc_info.value)

    def test_claim_invalid_quest(self, db_session, sample_pet):
        """领取不存在的任务"""
        qm = QuestManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            qm.claim_quest(sample_pet, "nonexistent_quest")
        assert "不存在" in str(exc_info.value)


class TestUpdateProgress:
    """测试更新进度"""

    def test_update_progress(self, db_session, sample_pet):
        """正常更新进度"""
        qm = QuestManager(db_session)

        # 找一个日常任务
        quests = qm.get_quests(sample_pet)
        daily_quest = None
        for quest in quests:
            if quest.definition.get("type") == "daily":
                daily_quest = quest
                break

        assert daily_quest is not None, "Should have at least one daily quest"
        initial_progress = daily_quest.progress
        quest_key = daily_quest.quest_key

        qm.update_progress(sample_pet, quest_key, 1)

        # 重新查询验证更新
        updated_quests = qm.get_quests(sample_pet)
        for quest in updated_quests:
            if quest.quest_key == quest_key:
                assert quest.progress == initial_progress + 1
                break

    def test_update_progress_caps_at_target(self, db_session, sample_pet):
        """进度不会超过目标值"""
        qm = QuestManager(db_session)
        quests = qm.get_quests(sample_pet)
        quest = quests[0]
        target = quest.definition.get("target", 10)

        # 多次更新超过目标值
        for _ in range(target + 5):
            qm.update_progress(sample_pet, quest.quest_key, 1)

        db_session.refresh(quest)
        assert quest.progress <= target


class TestAchievements:
    """测试成就"""

    def test_get_achievements(self, db_session, sample_pet):
        """获取成就列表"""
        qm = QuestManager(db_session)
        achievements = qm.get_achievements(sample_pet)

        assert len(achievements) > 0

        for ach in achievements:
            assert ach.definition is not None

    def test_achievement_initial_state(self, db_session, sample_pet):
        """成就初始状态"""
        qm = QuestManager(db_session)
        achievements = qm.get_achievements(sample_pet)

        for ach in achievements:
            assert ach.unlocked is False
            assert ach.progress >= 0


class TestQuestReset:
    """测试任务重置"""

    def test_quest_reset_on_expire(self, db_session, sample_pet):
        """过期任务重置"""
        qm = QuestManager(db_session)
        quests = qm.get_quests(sample_pet)
        quest = quests[0]

        # 设置为已完成
        quest.progress = quest.definition.get("target", 1)
        quest.completed = True
        quest.claimed = True

        # 设置为已过期（重置时间在过去）
        quest.reset_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        # 重新获取任务
        quests = qm.get_quests(sample_pet)
        db_session.refresh(quest)

        # 应该已重置
        assert quest.progress == 0
        assert quest.completed is False
        assert quest.claimed is False
