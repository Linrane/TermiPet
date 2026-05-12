"""状态面板 — 宠物状态的 rich 可视化 (Bilingual)"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from termipet.display.ascii_library import get_art, get_mood_emoji, get_hunger_emoji, get_species_color
from termipet.display.themes import t as theme
from termipet.locale import t as L
from termipet.models.pet import Pet


console = Console()


# ── 进度条渲染 ────────────────────────────────────────────────────────────────
def _bar(value: float, width: int = 20) -> str:
    """返回文本进度条"""
    filled = int(value / 100 * width)
    filled = max(0, min(width, filled))
    empty = width - filled

    if value >= 70:
        color = "green"
    elif value >= 40:
        color = "yellow"
    else:
        color = "red"

    bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
    return bar


def _stat_row(name: str, value: float, width: int = 18) -> str:
    return f"[bold]{name:<4}[/bold] {_bar(value, width)} [{_val_color(value)}]{value:5.1f}[/{_val_color(value)}]"


def _val_color(v: float) -> str:
    if v >= 70: return "green"
    if v >= 40: return "yellow"
    return "red"


def build_status_panel(pet: Pet, show_extended: bool = True) -> Panel:
    """构建宠物状态面板（rich Panel）"""
    species_color = get_species_color(pet.species_key)
    art_lines = get_art(pet.species_key, pet.stage)
    mood_e = get_mood_emoji(pet.happiness)
    hunger_e = get_hunger_emoji(pet.hunger)

    # ── 宠物图像列 ────────────────────────────────────────────────────────────
    art_text = Text()
    for line in art_lines:
        art_text.append(line + "\n", style=species_color)

    art_panel = Panel(
        Align.center(art_text),
        title=f"[bold {species_color}]{pet.name}[/]",
        border_style=species_color,
        width=24,
        padding=(0, 1),
    )

    # ── 属性列 ────────────────────────────────────────────────────────────────
    stats_lines = []
    stats_lines.append(_stat_row(L("data.stats.hunger"), pet.hunger))
    stats_lines.append(_stat_row(L("data.stats.happiness"), pet.happiness))
    stats_lines.append(_stat_row(L("data.stats.cleanliness"), pet.cleanliness))
    stats_lines.append(_stat_row(L("data.stats.health"), pet.health))

    if show_extended:
        stats_lines.append("─" * 28)
        stats_lines.append(_stat_row(L("data.stats.energy"), pet.energy))
        stats_lines.append(_stat_row(L("data.stats.intelligence"), pet.intelligence))
        stats_lines.append(_stat_row(L("data.stats.bond"), pet.bond))
        stats_lines.append(_stat_row(L("data.stats.constitution"), pet.constitution))

    stats_text = "\n".join(stats_lines)

    # ── 信息列 ────────────────────────────────────────────────────────────────
    stage_trans = L(f"data.stages.{pet.stage}", pet.stage)
    stage_colors = {
        "蛋": "dim", "幼年": "green", "少年": "cyan",
        "成年": "yellow", "巅峰": "bright_yellow",
        "传奇": "magenta", "远古": "bright_magenta",
        "Egg": "dim", "Youth": "green", "Teen": "cyan",
        "Adult": "yellow", "Peak": "bright_yellow",
        "Legend": "magenta", "Ancient": "bright_magenta",
    }
    stage_color = stage_colors.get(stage_trans, "white")

    now = datetime.now(timezone.utc)
    last_updated = pet.last_updated
    if last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)
    elapsed_min = int((now - last_updated).total_seconds() / 60)

    info_lines = [
        f"[bold]{L('status_panel.label_species')}[/bold]  {_get_species_name(pet.species_key)}",
        f"[bold]{L('status_panel.label_stage')}[/bold]  [{stage_color}]{stage_trans}[/{stage_color}]",
        f"[bold]{L('status_panel.label_personality')}[/bold]  {pet.personality}",
        f"[bold]{L('status_panel.label_talent')}[/bold]  [italic]{pet.talent or L('status_panel.unknown')}[/italic]",
        f"[bold]{L('status_panel.label_age')}[/bold]  {pet.age_days:.1f} {L('data.day_suffix')}",
        f"[bold]{L('status_panel.label_exp')}[/bold]  {pet.experience:.0f}",
        f"[bold]{L('status_panel.label_skill_points')}[/bold] {pet.skill_points}",
        "─" * 20,
        f"[bold yellow]{L('status_panel.coins_label')}[/bold yellow]  {pet.coins} 🪙",
        f"[bold bright_cyan]{L('status_panel.stardust_label')}[/bold bright_cyan]  {pet.stardust} ✨",
        "─" * 20,
        f"{L('status_panel.mood')}  {mood_e}  {L('status_panel.hunger_status')}  {hunger_e}",
        f"[dim]({elapsed_min}{L('status_panel.last_updated', minutes='')})[/dim]",
    ]

    info_text = "\n".join(info_lines)

    # ── 组合布局 ──────────────────────────────────────────────────────────────
    stats_panel = Panel(
        stats_text,
        title=f"[bold]{L('status_panel.stats_panel')}[/bold]",
        border_style=theme("border"),
        padding=(0, 1),
    )

    info_panel = Panel(
        info_text,
        title=f"[bold]{L('status_panel.info_panel')}[/bold]",
        border_style=theme("border"),
        padding=(0, 1),
    )

    # 构建完整面板
    inner_table = Table.grid(padding=(0, 1))
    inner_table.add_column(width=24)
    inner_table.add_column(width=32)
    inner_table.add_column(width=22)
    inner_table.add_row(art_panel, stats_panel, info_panel)

    outer_panel = Panel(
        inner_table,
        title=f"[bold {species_color}]✦ {L('status_panel.title', name=pet.name)} ✦[/bold {species_color}]",
        border_style=species_color,
        box=box.DOUBLE,
        padding=(0, 0),
    )
    return outer_panel


def live_status(pet: Pet, duration: int = 30) -> None:
    """动态刷新状态面板（duration 秒）"""
    from termipet.database import get_session
    from termipet.core.pet_manager import PetManager

    console.print(f"[dim]{L('status_panel.live_title')}[/dim]")
    start = time.time()

    try:
        with Live(console=console, refresh_per_second=1, screen=False) as live:
            while time.time() - start < duration:
                session = get_session()
                try:
                    from termipet.models.pet import Pet as PetModel
                    fresh_pet = session.query(PetModel).get(pet.id)
                    if fresh_pet:
                        pm = PetManager(session)
                        pm.apply_decay(fresh_pet)
                        session.commit()
                        panel = build_status_panel(fresh_pet)
                    else:
                        panel = Panel(f"[red]{L('status_panel.pet_lost')}[/red]")
                finally:
                    session.close()

                remaining = int(duration - (time.time() - start))
                footer = Text(
                    f" {L('status_panel.live_countdown', remaining=remaining)} ",
                    style="dim",
                )
                live.update(Panel(panel, subtitle=footer.plain, border_style="dim"))
                time.sleep(1)
    except KeyboardInterrupt:
        console.print(f"\n[dim]{L('status_panel.live_exited')}[/dim]")


def _get_species_name(key: str) -> str:
    return L(f"data.species.{key}", key)


def print_event_box(title: str, message: str, style: str = "cyan") -> None:
    """打印事件提示框"""
    console.print(Panel(
        f"[bold]{message}[/bold]",
        title=f"[bold {style}]{title}[/bold {style}]",
        border_style=style,
        padding=(0, 2),
    ))


def print_success(message: str) -> None:
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    console.print(f"[bold cyan]ℹ[/bold cyan] {message}")
