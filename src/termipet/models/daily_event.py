"""日常事件日志 ORM 模型"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from termipet.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DailyEventLog(Base):
    """日常事件日志 — 玩家离线期间宠物自主行动的记录"""
    __tablename__ = "daily_event_logs"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    event_key = Column(String(64), nullable=False)       # 事件标识
    category = Column(String(32), nullable=False)         # 事件大类
    title = Column(String(128), nullable=False)           # 事件标题
    summary = Column(Text, default="")                    # 简要描述
    detail = Column(Text, default="")                     # 详细描述
    result_json = Column(Text, default="{}")             # 事件结果 JSON
    occurred_at = Column(DateTime, default=_now)          # 事件发生时间
    read = Column(Boolean, default=False)                 # 是否已读

    pet = relationship("Pet", back_populates="daily_event_logs")

    @property
    def result(self) -> dict:
        return json.loads(self.result_json or "{}")

    @result.setter
    def result(self, val: dict):
        self.result_json = json.dumps(val, ensure_ascii=False)
