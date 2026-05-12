"""数据库初始化与会话管理"""
from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from termipet.config import DB_PATH, ensure_data_dir


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        ensure_data_dir()
        db_url = f"sqlite:///{DB_PATH}"
        _engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        # 开启 WAL 模式，提升并发读性能
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, _):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False
        )
    return _SessionLocal


def get_session() -> Session:
    """获取数据库会话（调用方负责 commit/close）"""
    return get_session_factory()()


def init_db() -> None:
    """创建所有表（首次运行时调用）"""
    # 延迟导入，确保所有模型都已注册
    from termipet.models import pet, item, home, skill, quest, maze, story, daily_event  # noqa: F401
    Base.metadata.create_all(get_engine())
