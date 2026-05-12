"""故事碎片 ORM 模型"""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from termipet.database import Base


# 故事碎片定义（运行时）
STORY_FRAGMENTS: dict[str, dict] = {
    "prologue_1":   {"title": "裂隙之始",       "order": 1,  "content": "数据裂隙出现于系统边界的那一天，第一只灵兽从虚空中睁开了眼睛……它看着你，像是认出了什么。"},
    "prologue_2":   {"title": "数字生命",       "order": 2,  "content": "灵兽不是普通的数据包。它们有意志、有情感，有时会在深夜的终端里发出轻微的呼吸声。"},
    "growth_1":     {"title": "破壳",           "order": 3,  "content": "蛋壳上出现了第一道裂纹。里面的生命在等待一个正确的时机。"},
    "growth_2":     {"title": "幼年时光",       "order": 4,  "content": "小小的它学会了第一个技能——用尾巴敲击键盘，发出叮叮当当的声音。"},
    "growth_3":     {"title": "青春期",         "order": 5,  "content": "它开始对迷宫感到好奇，每次你打开探险界面它都会凑过来盯着看。"},
    "growth_4":     {"title": "成年之约",       "order": 6,  "content": "「守护者，」它第一次开口，声音像是电路传来的回响，「谢谢你。」"},
    "maze_1":       {"title": "深渊入口",       "order": 7,  "content": "迷宫的第一层飘散着数据腐化的气息。石板上刻着某只远古灵兽留下的爪印。"},
    "maze_5":       {"title": "第五层的秘密",   "order": 8,  "content": "在第五层的隐秘角落，你们发现了一块残缺的石碑：「先行者在此，我已到达——」后面的字迹消失了。"},
    "maze_10":      {"title": "深渊核心",       "order": 9,  "content": "第十层的中央有一道光门。里面传来悠长的吟唱，像是某种古老的代码在运行。"},
    "species_cat":  {"title": "猫的秘密",       "order": 10, "content": "猫型灵兽来自数据裂隙的影子层，它们在明暗之间穿梭，看见别人看不见的东西。"},
    "species_mech": {"title": "机械之心",       "order": 11, "content": "机械型灵兽是被遗弃的古老程序，它们用钢铁外壳包裹着一颗渴望被理解的内核。"},
    "hidden_1":     {"title": "??????????",    "order": 99, "content": "「如果有一天我消失了，请记得——我们曾经在这片终端里，共同存在过。」"},
}


class StoryFragment(Base):
    """已解锁的故事碎片"""
    __tablename__ = "story_fragments"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    fragment_key = Column(String(64), nullable=False)
    unlocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    read = Column(Boolean, default=False)

    pet = relationship("Pet", back_populates="story_fragments")

    @property
    def definition(self) -> dict:
        return STORY_FRAGMENTS.get(self.fragment_key, {"title": "???", "content": "未知碎片"})
