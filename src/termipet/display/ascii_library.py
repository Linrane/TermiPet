"""ASCII 艺术库 — 宠物形态图"""
from __future__ import annotations

# 每个物种每个阶段的 ASCII 艺术
# key: species_key + "_" + stage (若无特定阶段则用默认)
ASCII_ARTS: dict[str, list[str]] = {

    # ── 猫型 ─────────────────────────────────────────────────────────────────
    "cat_蛋": [
        "    .--.",
        "   (    )",
        "    `--'",
        "    ~~~~",
    ],
    "cat_幼年": [
        "  /\\_/\\  ",
        " ( o.o ) ",
        "  > ^ <  ",
        "  |   |  ",
    ],
    "cat_少年": [
        "  /\\_/\\  ",
        " ( ^.^ ) ",
        "  > v <  ",
        " /|   |\\ ",
    ],
    "cat_成年": [
        "  /\\_/\\   ",
        " ( *.* )  ",
        "  > ^ <   ",
        " / '  ' \\ ",
        "|  |  |  |",
    ],
    "cat_巅峰": [
        "    /\\_/\\  ",
        "   (  *.* )",
        "  / > ^ < \\",
        " |  |   |  |",
        "  \\_______/ ",
    ],
    "cat_传奇": [
        " ~  /\\_/\\  ~ ",
        " ~( ✦.✦ )~ ",
        "  > ♪ ^ <  ",
        " /  |   |  \\",
        "|   |   |   |",
    ],
    "cat_远古": [
        "✦ ✦  /\\_/\\  ✦ ✦",
        " ✦ (  ✦.✦  ) ✦ ",
        "    > ♛ ^ <    ",
        "   / ═══════ \\  ",
        "  |  |     |  | ",
    ],

    # ── 犬型 ─────────────────────────────────────────────────────────────────
    "dog_蛋": [
        "   .--.",
        "  ( ww )",
        "   '--'",
        "   ~~~~",
    ],
    "dog_幼年": [
        "  / 0 0 \\",
        " |  ___  |",
        "  \\_____/",
        "  /|   |\\",
    ],
    "dog_成年": [
        "  / o o \\  ",
        " |  ___  | ",
        "  \\_____/  ",
        "  / | | \\  ",
        " /  |_|  \\ ",
    ],
    "dog_传奇": [
        " ~/ ★ ★ \\~",
        " |  ___  | ",
        "  \\_____/  ",
        " /  |   |  \\",
        "|   |   |   |",
    ],

    # ── 鸟型 ─────────────────────────────────────────────────────────────────
    "bird_蛋": [
        "   .---.",
        "  ( egg )",
        "   '---'",
        "    ~~~~",
    ],
    "bird_幼年": [
        "  _   _",
        " (o) (o)",
        "  \\_^_/",
        "   |_|",
        "  /   \\",
    ],
    "bird_成年": [
        "   __|__",
        "  (o) (o)",
        "   \\_^_/",
        "  //   \\\\",
        " //     \\\\",
    ],
    "bird_传奇": [
        " ✦  __|__  ✦",
        "   (✦) (✦) ",
        "    \\_✦_/  ",
        " ~~//   \\\\~~",
        "  //     \\\\  ",
    ],

    # ── 机械型 ───────────────────────────────────────────────────────────────
    "mech_蛋": [
        "  [====]",
        "  | .. |",
        "  [====]",
        "   ~~~~",
    ],
    "mech_幼年": [
        "  [o_o]",
        " /|___|\\ ",
        "  |   |",
        " _|___|_",
    ],
    "mech_成年": [
        "  [===]  ",
        " [0 _ 0] ",
        " |=====| ",
        " |     | ",
        " |_|_|_| ",
    ],
    "mech_传奇": [
        " ▓[═══]▓ ",
        " [★ _ ★] ",
        " |══════| ",
        " |  CPU  | ",
        " |▓▓▓▓▓▓| ",
    ],

    # ── 神秘型 ───────────────────────────────────────────────────────────────
    "mystery_蛋": [
        "   ~.~",
        "  (???)",
        "   ~'~",
        "  ·····",
    ],
    "mystery_幼年": [
        "  /~·~\\",
        " ( ? . ? )",
        "  \\_~_/",
        "  ·····",
    ],
    "mystery_成年": [
        "  ∴/~·~\\∴",
        " ( ✧.✧ )",
        "  \\_~_/ ",
        " ∴ | | ∴",
        "  .|   |.",
    ],
    "mystery_传奇": [
        "∴✦∴/~·~\\∴✦∴",
        "  ( ✦.✦ ) ",
        " ∴ \\_~_/ ∴",
        "   | | | | ",
        " ∴.|   |.∴",
    ],
    "mystery_远古": [
        "✦∴✦∴/~~~\\∴✦∴✦",
        "   ( ✦∴✦ )  ",
        "  ∴ \\_∴_/ ∴ ",
        "  ✦ | ∴ | ✦ ",
        " ∴✦.|   |.✦∴",
    ],
}

# 通用未知形态
FALLBACK_ART = [
    "  .----.",
    " ( ?  ? )",
    "  '----'",
    "   ~~~~",
]


def get_art(species_key: str, stage: str) -> list[str]:
    """获取指定物种阶段的 ASCII 艺术，无匹配时返回通用图"""
    key = f"{species_key}_{stage}"
    if key in ASCII_ARTS:
        return ASCII_ARTS[key]

    # 回退：找同物种最接近的阶段
    stages = ["蛋", "幼年", "少年", "成年", "巅峰", "传奇", "远古"]
    target_idx = stages.index(stage) if stage in stages else 0
    for i in range(target_idx, -1, -1):
        fallback_key = f"{species_key}_{stages[i]}"
        if fallback_key in ASCII_ARTS:
            return ASCII_ARTS[fallback_key]

    return FALLBACK_ART


def render_art(species_key: str, stage: str, color: str = "cyan") -> str:
    """返回带 rich markup 的 ASCII 艺术字符串"""
    lines = get_art(species_key, stage)
    colored_lines = [f"[{color}]{line}[/{color}]" for line in lines]
    return "\n".join(colored_lines)


# 状态表情符号
MOOD_EMOJI = {
    (80, 101): "😊",  # 非常快乐
    (60, 80):  "🙂",  # 快乐
    (40, 60):  "😐",  # 普通
    (20, 40):  "😕",  # 不开心
    (0,  20):  "😢",  # 悲伤
}

HUNGER_EMOJI = {
    (80, 101): "🍖",  # 很饱
    (60, 80):  "🍗",  # 饱
    (40, 60):  "😋",  # 有点饿
    (20, 40):  "🍽️",  # 饿
    (0,  20):  "😖",  # 非常饿
}


def get_mood_emoji(value: float) -> str:
    for (lo, hi), emoji in MOOD_EMOJI.items():
        if lo <= value < hi:
            return emoji
    return "❓"


def get_hunger_emoji(value: float) -> str:
    for (lo, hi), emoji in HUNGER_EMOJI.items():
        if lo <= value < hi:
            return emoji
    return "❓"


# 物种颜色映射
SPECIES_COLORS = {
    "cat":     "cyan",
    "dog":     "yellow",
    "bird":    "green",
    "mech":    "blue",
    "mystery": "magenta",
}

def get_species_color(species_key: str) -> str:
    return SPECIES_COLORS.get(species_key, "white")
