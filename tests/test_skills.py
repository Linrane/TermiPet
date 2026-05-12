"""SkillSystem 测试"""
import pytest

from termipet.core.skill_system import SkillSystem


class TestGetAvailableSkills:
    """测试获取可用技能"""

    def test_get_available_skills(self, db_session, sample_pet):
        """获取可用技能列表"""
        ss = SkillSystem(db_session)
        skills = ss.get_available_skills(sample_pet)

        assert len(skills) > 0

        for skill in skills:
            assert "key" in skill
            assert "name" in skill
            assert "learned" in skill

    def test_skills_species_filter(self, db_session, sample_pet):
        """猫型宠物有专属技能"""
        ss = SkillSystem(db_session)
        skills = ss.get_available_skills(sample_pet)

        skill_keys = [s["key"] for s in skills]
        # 猫型专属技能
        cat_specific = ["shadow_step", "purr_therapy"]
        for key in cat_specific:
            assert key in skill_keys

    def test_skills_not_learned_initially(self, db_session, sample_pet):
        """初始时技能未学习"""
        ss = SkillSystem(db_session)
        skills = ss.get_available_skills(sample_pet)

        for skill in skills:
            assert skill["learned"] is False
            assert skill["level"] == 0


class TestLearnSkill:
    """测试学习技能"""

    def test_learn_skill(self, db_session, sample_pet):
        """学习技能"""
        ss = SkillSystem(db_session)

        # 给宠物一些技能点
        sample_pet.skill_points = 10
        db_session.commit()

        result = ss.learn_skill(sample_pet, "quick_heal")

        assert result["action"] == "学习"
        assert result["level"] == 1
        assert result["skill"] == "急救"

    def test_learn_skill_by_name(self, db_session, sample_pet):
        """按名字学习技能"""
        ss = SkillSystem(db_session)
        sample_pet.skill_points = 10
        db_session.commit()

        result = ss.learn_skill(sample_pet, "急救")

        assert result["action"] == "学习"

    def test_learn_insufficient_points(self, db_session, sample_pet):
        """技能点不足"""
        ss = SkillSystem(db_session)
        sample_pet.skill_points = 0  # 急救需要1点
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            ss.learn_skill(sample_pet, "quick_heal")
        assert "技能点不足" in str(exc_info.value)

    def test_learn_unknown_skill(self, db_session, sample_pet):
        """未知技能"""
        ss = SkillSystem(db_session)
        sample_pet.skill_points = 100
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            ss.learn_skill(sample_pet, "nonexistent_skill_xyz")
        assert "未知技能" in str(exc_info.value)

    def test_learn_species_restricted(self, db_session, dog_pet):
        """物种限制"""
        ss = SkillSystem(db_session)
        dog_pet.skill_points = 100
        db_session.commit()

        # 猫型专属技能，犬型不能学
        with pytest.raises(ValueError) as exc_info:
            ss.learn_skill(dog_pet, "shadow_step")
        assert "仅限" in str(exc_info.value)

    def test_learn_egg_stage(self, db_session, egg_pet):
        """蛋期不能学习"""
        ss = SkillSystem(db_session)
        egg_pet.skill_points = 100
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            ss.learn_skill(egg_pet, "quick_heal")
        assert "还在蛋里" in str(exc_info.value)


class TestUpgradeSkill:
    """测试升级技能"""

    def test_upgrade_skill(self, db_session, sample_pet):
        """升级技能"""
        ss = SkillSystem(db_session)
        # 急救技能cost=1，学习后升级费用=1*(1+1)=2
        sample_pet.skill_points = 10  # 足够学习(1)和升级(2)
        db_session.commit()

        # 先学习
        result1 = ss.learn_skill(sample_pet, "quick_heal")
        assert result1["action"] == "学习"
        assert result1["level"] == 1

        # 再升级 (learn_skill 也用于升级)
        result2 = ss.learn_skill(sample_pet, "quick_heal")

        assert result2["action"] == "升级"
        assert result2["level"] == 2

    def test_max_level(self, db_session, sample_pet):
        """满级不能再升级"""
        ss = SkillSystem(db_session)

        # 直接设置为满级
        from termipet.models.skill import Skill
        skill = Skill(pet_id=sample_pet.id, skill_key="quick_heal", level=5)
        db_session.add(skill)
        sample_pet.skill_points = 100
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            ss.learn_skill(sample_pet, "quick_heal")
        assert "最大等级" in str(exc_info.value)


class TestPassiveBonuses:
    """测试被动加成"""

    def test_get_passive_bonuses(self, db_session, sample_pet):
        """获取被动技能加成"""
        ss = SkillSystem(db_session)

        # 先学习一些被动技能
        sample_pet.skill_points = 100
        db_session.commit()

        ss.learn_skill(sample_pet, "sharp_mind")  # 被动技能
        ss.learn_skill(sample_pet, "tough_skin")  # 被动技能

        bonuses = ss.get_passive_bonuses(sample_pet)

        assert len(bonuses) > 0

    def test_no_skills(self, db_session, sample_pet):
        """没有技能时返回空"""
        ss = SkillSystem(db_session)
        bonuses = ss.get_passive_bonuses(sample_pet)
        assert bonuses == {}
