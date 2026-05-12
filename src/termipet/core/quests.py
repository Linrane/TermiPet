"""任务与成就管理器"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.quest import Quest, Achievement, QUEST_DEFINITIONS, ACHIEVEMENT_DEFINITIONS


def _utcnow():
    return datetime.now(timezone.utc)


class QuestManager:
    def __init__(self, session: Session):
        self.session = session

    def get_quests(self, pet: Pet) -> list[Quest]:
        """获取所有任务，自动重置已过期任务"""
        quests = self.session.query(Quest).filter_by(pet_id=pet.id).all()
        now = _utcnow()
        changed = False

        for q in quests:
            if q.reset_at:
                reset_at = q.reset_at
                if reset_at.tzinfo is None:
                    reset_at = reset_at.replace(tzinfo=timezone.utc)
                if now >= reset_at and (q.completed or q.progress > 0):
                    defn = q.definition
                    q.progress = 0
                    q.completed = False
                    q.claimed = False
                    # 计算下一次重置时间
                    if defn.get("type") == "daily":
                        q.reset_at = reset_at + timedelta(days=1)
                    else:
                        q.reset_at = reset_at + timedelta(weeks=1)
                    changed = True

        if changed:
            self.session.commit()

        return quests

    def claim_quest(self, pet: Pet, quest_key: str) -> dict:
        """领取任务奖励"""
        q = self.session.query(Quest).filter_by(pet_id=pet.id, quest_key=quest_key).first()
        if q is None:
            raise ValueError(f"任务 '{quest_key}' 不存在。")
        if not q.completed:
            defn = q.definition
            raise ValueError(
                f"任务「{defn.get('name', quest_key)}」尚未完成 "
                f"（{q.progress}/{defn.get('target', '?')}）。"
            )
        if q.claimed:
            raise ValueError(f"任务「{q.definition.get('name', quest_key)}」奖励已领取。")

        defn = q.definition
        q.claimed = True

        coins = defn.get("coins", 0)
        stardust = defn.get("stardust", 0)
        items = defn.get("items", [])

        pet.coins += coins
        pet.stardust += stardust

        self.session.commit()
        return {"name": defn.get("name"), "coins": coins, "stardust": stardust, "items": items}

    def update_progress(self, pet: Pet, quest_key: str, delta: int) -> None:
        q = self.session.query(Quest).filter_by(pet_id=pet.id, quest_key=quest_key).first()
        if q and not q.completed:
            defn = q.definition
            q.progress = min(q.progress + delta, defn.get("target", 9999))
            if q.progress >= defn.get("target", 9999):
                q.completed = True

    def get_achievements(self, pet: Pet) -> list[Achievement]:
        return self.session.query(Achievement).filter_by(pet_id=pet.id).all()
