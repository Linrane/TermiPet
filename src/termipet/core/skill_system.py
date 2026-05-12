"""技能系统 — 学习、升级、查询"""
from __future__ import annotations

from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.skill import Skill, SKILL_DEFINITIONS


class SkillSystem:
    def __init__(self, session: Session):
        self.session = session

    def get_available_skills(self, pet: Pet) -> list[dict]:
        """获取宠物可学习的技能列表"""
        species_key = pet.species_key
        result = []
        learned_keys = {s.skill_key for s in pet.skills}

        for key, defn in SKILL_DEFINITIONS.items():
            # 检查物种限制
            species_restriction = defn.get("species")
            if species_restriction and species_key not in species_restriction:
                continue

            learned = self.session.query(Skill).filter_by(pet_id=pet.id, skill_key=key).first()
            result.append({
                "key": key,
                "name": defn["name"],
                "type": defn["type"],
                "cost": defn["cost"],
                "desc": defn["desc"],
                "learned": learned is not None,
                "level": learned.level if learned else 0,
                "max_level": 5,
            })
        return result

    def learn_skill(self, pet: Pet, skill_key: str) -> dict:
        """学习或升级技能"""
        # 支持名字匹配
        actual_key = skill_key
        if skill_key not in SKILL_DEFINITIONS:
            for k, d in SKILL_DEFINITIONS.items():
                if d["name"] == skill_key or skill_key in d["name"]:
                    actual_key = k
                    break
            else:
                names = [d["name"] for d in SKILL_DEFINITIONS.values()]
                raise ValueError(
                    f"未知技能 '{skill_key}'。\n"
                    f"可用技能：{', '.join(names)}\n"
                    f"使用 [bold]pet skill list[/] 查看完整技能树。"
                )

        defn = SKILL_DEFINITIONS[actual_key]

        # 检查物种限制
        species_restriction = defn.get("species")
        if species_restriction and pet.species_key not in species_restriction:
            restrict_str = "、".join(species_restriction)
            raise ValueError(f"技能「{defn['name']}」仅限 {restrict_str} 物种学习。")

        # 检查阶段限制（幼年才能学技能）
        if pet.stage == "蛋":
            raise ValueError("宠物还在蛋里，无法学习技能！等它孵化后再来吧。")

        existing = self.session.query(Skill).filter_by(pet_id=pet.id, skill_key=actual_key).first()
        if existing and existing.level >= 5:
            raise ValueError(f"技能「{defn['name']}」已达到最大等级 5！")

        cost = defn["cost"]
        if existing:
            cost = defn["cost"] * (existing.level + 1)  # 升级费用递增

        if pet.skill_points < cost:
            raise ValueError(
                f"技能点不足！学习「{defn['name']}」需要 {cost} 点，当前只有 {pet.skill_points} 点。\n"
                f"通过互动、探险、成长来获得技能点。"
            )

        pet.skill_points -= cost

        if existing:
            existing.level += 1
            result = {"action": "升级", "skill": defn["name"], "level": existing.level, "cost": cost}
        else:
            skill = Skill(pet_id=pet.id, skill_key=actual_key, level=1)
            self.session.add(skill)
            result = {"action": "学习", "skill": defn["name"], "level": 1, "cost": cost}

        self.session.commit()
        return result

    def get_passive_bonuses(self, pet: Pet) -> dict:
        """汇总所有被动技能加成"""
        bonuses = {}
        for skill in pet.skills:
            if skill.skill_key not in SKILL_DEFINITIONS:
                continue
            defn = SKILL_DEFINITIONS[skill.skill_key]
            if defn["type"] == "passive":
                for k, v in defn["effect"].items():
                    if isinstance(v, (int, float)):
                        bonuses[k] = bonuses.get(k, 0) + v * skill.level
                    else:
                        bonuses[k] = v
        return bonuses
