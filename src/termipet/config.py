"""配置管理模块 — 读取和保存用户配置"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import toml
except ImportError:
    toml = None  # type: ignore

# ─── 路径 ───────────────────────────────────────────────────────────────────
APP_NAME = "termipet"
DATA_DIR = Path(os.environ.get("TERMIPET_DATA", Path.home() / ".termipet"))
DB_PATH = DATA_DIR / "termipet.db"
CONFIG_PATH = DATA_DIR / "config.toml"
LOG_PATH = DATA_DIR / "events.log"

# ─── 默认配置 ────────────────────────────────────────────────────────────────
DEFAULT_CONFIG: dict[str, Any] = {
    "theme": "cyberpunk",          # cyberpunk / pastel / minimal
    "language": "zh",              # zh / en
    "auto_save": True,
    "notification": True,
    "decay_multiplier": 1.0,       # 属性衰减速度倍率（方便测试时调快）
    "animation_speed": "normal",   # fast / normal / slow
}


def ensure_data_dir() -> None:
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """加载配置文件，不存在则创建默认配置"""
    ensure_data_dir()
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    if toml is None:
        return DEFAULT_CONFIG.copy()

    try:
        cfg = toml.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        # 合并默认值（保证新字段向后兼容）
        merged = {**DEFAULT_CONFIG, **cfg}
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg: dict[str, Any]) -> None:
    """保存配置到文件"""
    ensure_data_dir()
    if toml is None:
        return
    try:
        CONFIG_PATH.write_text(
            toml.dumps(cfg), encoding="utf-8"
        )
    except Exception:
        pass


def get(key: str, default: Any = None) -> Any:
    """获取单个配置项"""
    return load_config().get(key, default)
