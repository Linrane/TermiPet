"""主题配置"""
from __future__ import annotations

THEMES = {
    "cyberpunk": {
        "primary":    "bright_cyan",
        "secondary":  "bright_magenta",
        "accent":     "bright_yellow",
        "warning":    "yellow",
        "danger":     "red",
        "success":    "bright_green",
        "muted":      "dim",
        "border":     "cyan",
        "bar_full":   "cyan",
        "bar_empty":  "dim",
        "title":      "bold bright_cyan",
        "panel_bg":   "",
    },
    "pastel": {
        "primary":    "pink3",
        "secondary":  "light_sky_blue1",
        "accent":     "pale_turquoise1",
        "warning":    "gold1",
        "danger":     "light_coral",
        "success":    "pale_green1",
        "muted":      "grey70",
        "border":     "pink3",
        "bar_full":   "pink3",
        "bar_empty":  "grey30",
        "title":      "bold pink3",
        "panel_bg":   "",
    },
    "minimal": {
        "primary":    "white",
        "secondary":  "bright_white",
        "accent":     "white",
        "warning":    "yellow",
        "danger":     "red",
        "success":    "green",
        "muted":      "dim",
        "border":     "white",
        "bar_full":   "white",
        "bar_empty":  "dim",
        "title":      "bold white",
        "panel_bg":   "",
    },
}

_current_theme_name = "cyberpunk"


def set_theme(name: str) -> None:
    global _current_theme_name
    if name in THEMES:
        _current_theme_name = name


def get_theme() -> dict[str, str]:
    return THEMES.get(_current_theme_name, THEMES["cyberpunk"])


def t(key: str) -> str:
    """快捷获取当前主题的颜色值"""
    return get_theme().get(key, "white")
