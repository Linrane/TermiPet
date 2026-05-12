"""i18n translation engine — zero-dependency dictionary-based localization"""
from __future__ import annotations

_current_locale: dict = {}
_lang: str = "zh"


def _deep_get(d: dict, key: str, default: str | None = None) -> str:
    """Navigate nested dict with dot notation: 'cmd.pet.adopt_prompt'"""
    keys = key.split(".")
    node = d
    for k in keys:
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return default if default is not None else key
    return str(node) if not isinstance(node, dict) else (default if default is not None else key)


def set_locale(lang: str | None = None) -> None:
    """Switch language. Auto-reads from config if lang is None."""
    global _lang, _current_locale
    if lang is None:
        from termipet.config import get
        lang = get("language", "zh")
    _lang = lang
    if lang == "en":
        from termipet.locale.en import STRINGS
    else:
        from termipet.locale.zh import STRINGS
    _current_locale = STRINGS


def get_lang() -> str:
    return _lang


def t(key: str, default: str | None = None, **kwargs) -> str:
    """Translate a key, with optional format kwargs.

    Usage: t("cmd.pet.feed_full", name="Fluffy")
    Falls back to key itself (or `default`) if not found.
    """
    text = _deep_get(_current_locale, key)
    # Check if text was resolved (not a dict and not equal to key)
    if isinstance(text, dict):
        text = key
    if text == key and default is not None:
        text = default
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    return text


# Module-level shorthand
_t = t
