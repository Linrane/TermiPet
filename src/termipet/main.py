"""TermiPet 2.0 — CLI 主入口"""
from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


# ── 全局初始化（每次启动时执行） ──────────────────────────────────────────────
def _startup_init() -> None:
    """确保数据库和种子数据已初始化"""
    try:
        from termipet.utils.seeds import initialize_game
        initialize_game()
    except Exception as e:
        console.print(f"[yellow]⚠ 初始化警告：{e}[/yellow]")


# ── 启动横幅 ─────────────────────────────────────────────────────────────────
BANNER = r"""
  ______  _________  ______  __  __  _____  ____   _____  ______
 /_  __/ / _____  / / ___  |/  |/  |/_  _/ / __ \ / __  |/_  __/
  / /   / /____/ / / /__/ // /|_/ /  / /  / /_/ // //_/  / /
 /_/   /_______/  \____/ /_/    /_/  /_/  / .___//_/     /_/
                                         /_/
"""

BANNER_SIMPLE = "✦ TermiPet 2.0  终端电子宠物·浩瀚版 ✦"


def print_banner():
    console.print(Panel(
        f"[bold cyan]{BANNER_SIMPLE}[/bold cyan]\n"
        f"[dim]数字生命守护者，在终端中书写灵兽的传说[/dim]",
        border_style="cyan",
        box=box.DOUBLE,
        padding=(0, 2),
    ))


# ══════════════════════════════════════════════════════════════════════════════
#  主命令组
# ══════════════════════════════════════════════════════════════════════════════
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.pass_context
def cli(ctx):
    """
    TermiPet 2.0 — 终端电子宠物·浩瀚版

    \b
    快速开始：
      pet adopt cat --name 小橘     领养一只猫型灵兽
      pet status                    查看宠物状态
      pet feed                      喂食
      pet play                      玩耍
      pet adventure start           开始探险

    使用 pet <命令> --help 查看详细用法。
    """
    _startup_init()

    if ctx.invoked_subcommand is None:
        print_banner()
        console.print()
        console.print(ctx.get_help())


# ── 注册子命令 ────────────────────────────────────────────────────────────────
def _register_commands():
    try:
        from termipet.commands.pet_cmd import (
            adopt_cmd, status_cmd, feed_cmd, play_cmd,
            clean_cmd, sleep_cmd, train_cmd, skill_group,
        )
        from termipet.commands.home_cmd import home_group
        from termipet.commands.adventure_cmd import adventure_group
        from termipet.commands.shop_cmd import shop_group, inventory_cmd
        from termipet.commands.social_cmd import (
            quests_cmd, achievements_cmd, story_cmd, collection_cmd
        )

        cli.add_command(adopt_cmd,       "adopt")
        cli.add_command(status_cmd,      "status")
        cli.add_command(feed_cmd,        "feed")
        cli.add_command(play_cmd,        "play")
        cli.add_command(clean_cmd,       "clean")
        cli.add_command(sleep_cmd,       "sleep")
        cli.add_command(train_cmd,       "train")
        cli.add_command(skill_group,     "skill")
        cli.add_command(home_group,      "home")
        cli.add_command(adventure_group, "adventure")
        cli.add_command(shop_group,      "shop")
        cli.add_command(inventory_cmd,   "inventory")
        cli.add_command(quests_cmd,      "quests")
        cli.add_command(achievements_cmd,"achievements")
        cli.add_command(story_cmd,       "story")
        cli.add_command(collection_cmd,  "collection")

    except ImportError as e:
        console.print(f"[red]命令加载失败：{e}[/red]")
        sys.exit(1)


_register_commands()


# ── 额外便捷命令 ──────────────────────────────────────────────────────────────
@cli.command("info")
def info_cmd():
    """显示游戏信息和帮助"""
    print_banner()
    console.print()

    from termipet.database import get_session
    from termipet.core.pet_manager import PetManager
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.get_active_pet()
        if pet:
            from termipet.display.status_panel import build_status_panel
            from termipet.core.pet_manager import PetManager as PM
            pm2 = PM(session)
            pm2.apply_decay(pet)
            session.commit()
            panel = build_status_panel(pet, show_extended=False)
            console.print(panel)
        else:
            console.print("[dim]还没有宠物，使用 [bold]pet adopt <物种>[/bold] 领养一只灵兽！[/dim]")
            console.print("[dim]可用物种：cat、dog、bird、mech、mystery[/dim]")
    finally:
        session.close()


@cli.command("list-pets")
def list_pets_cmd():
    """查看所有已领养的宠物"""
    from termipet.database import get_session
    from termipet.models.pet import Pet
    from rich.table import Table

    session = get_session()
    try:
        pets = session.query(Pet).all()
        if not pets:
            console.print("[dim]还没有任何宠物。[/dim]")
            return

        table = Table(title="🐾 已领养的灵兽", box=box.ROUNDED, border_style="cyan")
        table.add_column("ID", width=4)
        table.add_column("名字", style="bold", width=12)
        table.add_column("物种", width=10)
        table.add_column("阶段", width=8)
        table.add_column("年龄", width=8)
        table.add_column("状态", width=8)

        for p in pets:
            active = "[bold green]活跃[/bold green]" if p.is_active else "[dim]休眠[/dim]"
            from termipet.display.status_panel import _get_species_name
            table.add_row(
                str(p.id), p.name,
                _get_species_name(p.species_key),
                p.stage,
                f"{p.age_days:.1f}天",
                active,
            )

        console.print(table)
    finally:
        session.close()


@cli.command("switch")
@click.argument("pet_id", type=int)
def switch_cmd(pet_id: int):
    """切换活跃宠物（指定ID）"""
    from termipet.database import get_session
    from termipet.models.pet import Pet

    session = get_session()
    try:
        # 取消当前活跃
        current = session.query(Pet).filter_by(is_active=True).first()
        if current:
            current.is_active = False

        target = session.get(Pet, pet_id)
        if target is None:
            console.print(f"[red]✗ 没有 ID 为 {pet_id} 的宠物。使用 pet list-pets 查看所有宠物。[/red]")
            return

        target.is_active = True
        session.commit()
        console.print(f"[green]✓ 已切换到「{target.name}」。[/green]")
    finally:
        session.close()


if __name__ == "__main__":
    cli()
