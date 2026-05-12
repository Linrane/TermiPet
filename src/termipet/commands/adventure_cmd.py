"""探险命令 — adventure start/move/auto/retreat/status"""
from __future__ import annotations

import sys
import time

import click
from rich.console import Console
from rich.panel import Panel
from rich import box

from termipet.database import get_session
from termipet.core.adventure import AdventureManager
from termipet.core.pet_manager import PetManager
from termipet.display.maze_ui import print_maze, print_battle_animation, print_loot_animation
from termipet.display.status_panel import (
    print_success, print_error, print_warning, print_info, console
)


def safe_cmd(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print_error(str(e))
            sys.exit(0)
        except Exception as e:
            print_error(f"发生了一个意外错误：{e}")
            sys.exit(0)
    return wrapper


@click.group("adventure")
def adventure_group():
    """探险相关命令"""
    pass


@adventure_group.command("start")
@click.option("--depth", "-d", default=1, type=int, help="从第几层开始（1-20）")
@safe_cmd
def adventure_start_cmd(depth: int):
    """开始新探险"""
    depth = max(1, min(depth, 20))

    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        am = AdventureManager(session)

        # 检查是否已有进行中的探险
        existing = am.get_state(pet)
        if existing:
            if not click.confirm(
                f"你已有一个进行中的探险（第 {existing.floor} 层）。开始新探险会放弃当前进度，确定吗？",
                default=False
            ):
                print_info("使用 [bold]pet adventure move <方向>[/bold] 继续当前探险。")
                return

        with console.status(f"[cyan]进入迷宫第 {depth} 层……[/cyan]", spinner="dots"):
            time.sleep(1.2)
            state = am.start(pet, start_floor=depth)

        console.print()
        print_maze(state, pet_name=pet.name)

        console.print(Panel(
            f"[bold cyan]{pet.name}[/bold cyan] 进入了迷宫第 [bold]{depth}[/bold] 层！\n"
            f"[dim]使用方向键移动：[bold]pet adventure move w/a/s/d[/bold]\n"
            f"到达出口 [bold yellow]E[/bold yellow] 进入下一层，使用 [bold]pet adventure retreat[/bold] 撤退[/dim]",
            title="🗺️ 探险开始！",
            border_style="cyan",
            padding=(0, 2),
        ))
    finally:
        session.close()


@adventure_group.command("move")
@click.argument("direction")
@safe_cmd
def adventure_move_cmd(direction: str):
    """移动（w上 s下 a左 d右）"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        am = AdventureManager(session)

        result = am.move(pet, direction)
        session.commit()

        if not result.get("moved"):
            print_warning(result.get("reason", "无法移动。"))
            return

        event = result.get("event", {})
        event_type = event.get("type", "empty")
        event_msg = event.get("message", "")

        # 显示迷宫
        state = am.get_state(pet)
        if state:
            print_maze(state, pet_name=pet.name, event_msg=event_msg)

        # 战斗动画
        if event_type == "battle":
            print_battle_animation(
                event.get("pet_choice", "攻击"),
                event.get("enemy_choice", "攻击"),
                event.get("result", "平局"),
            )

        # 事件消息
        if event_msg and event_type != "empty":
            _print_event_styled(event_type, event_msg)

        # 致命事件
        if event_type in ("trap_fatal", "defeated"):
            print_warning(f"{pet.name} 已失去意识，自动撤退中……")
            loot_result = am.retreat(pet)
            if loot_result.get("loot"):
                print_loot_animation(loot_result["loot"])
            session.commit()

        # 进入新层
        if event_type == "exit":
            console.print(f"\n[bold bright_yellow]进入第 {event.get('new_floor')} 层！[/bold bright_yellow]")

    finally:
        session.close()


@adventure_group.command("auto")
@click.option("--steps", "-s", default=10, type=int, help="自动移动步数（最多20）")
@safe_cmd
def adventure_auto_cmd(steps: int):
    """自动探险（AI 控制移动）"""
    steps = max(1, min(steps, 20))

    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        am = AdventureManager(session)

        state = am.get_state(pet)
        if state is None:
            raise ValueError("没有进行中的探险！使用 [bold]pet adventure start[/bold] 开始。")

        console.print(f"[cyan]自动探险开始，最多 {steps} 步……[/cyan]")

        for i, result in enumerate(am.auto_explore(pet, steps=steps)):
            time.sleep(0.4)

            if not result.get("moved"):
                console.print(f"[yellow]第{i+1}步：{result.get('reason', '停止')}[/yellow]")
                break

            event = result.get("event", {})
            event_type = event.get("type", "empty")
            event_msg = event.get("message", "")

            pos = result.get("pos", (0, 0))
            floor_n = result.get("floor", 1)
            console.print(f"  [dim]步{i+1}[/dim] [{floor_n}F ({pos[0]},{pos[1]})] ", end="")

            if event_msg and event_type != "empty":
                console.print(event_msg)
            else:
                console.print("[dim]……[/dim]")

            if event_type in ("trap_fatal", "defeated", "exit"):
                if event_type == "exit":
                    console.print(f"[bold bright_yellow]进入第 {event.get('new_floor')} 层！[/bold bright_yellow]")
                break

        session.commit()

        # 最终状态
        state = am.get_state(pet)
        if state:
            console.print()
            print_maze(state, pet_name=pet.name)

    finally:
        session.close()


@adventure_group.command("retreat")
@safe_cmd
def adventure_retreat_cmd():
    """撤出迷宫，带走战利品"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        am = AdventureManager(session)

        with console.status("[cyan]正在撤退……[/cyan]", spinner="dots"):
            time.sleep(0.8)
            result = am.retreat(pet)

        loot = result.get("loot", [])
        loot_str = "  ".join(loot) if loot else "空手而归"

        console.print(Panel(
            f"[bold]从第 {result['floor']} 层安全撤退！[/bold]\n"
            f"带回战利品：{loot_str}",
            title="🏃 撤退成功",
            border_style="yellow",
            padding=(0, 2),
        ))

        if loot:
            print_loot_animation(loot)
    finally:
        session.close()


@adventure_group.command("status")
@safe_cmd
def adventure_status_cmd():
    """查看当前探险状态"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        am = AdventureManager(session)

        state = am.get_state(pet)
        if state is None:
            print_info("当前没有进行中的探险。使用 [bold]pet adventure start[/bold] 开始一次探险。")
            return

        print_maze(state, pet_name=pet.name)
    finally:
        session.close()


def _print_event_styled(event_type: str, message: str) -> None:
    STYLES = {
        "chest":         ("yellow",  "📦 宝箱！"),
        "trap":          ("red",     "⚠ 陷阱！"),
        "trap_evaded":   ("green",   "✨ 躲避！"),
        "trap_fatal":    ("red",     "💀 危险！"),
        "battle":        ("magenta", "⚔ 战斗！"),
        "puzzle":        ("cyan",    "🔮 谜题！"),
        "exit":          ("bright_yellow", "🚪 出口！"),
        "shop":          ("cyan",    "🛒 商店！"),
        "story":         ("magenta", "📖 故事！"),
    }
    style, title = STYLES.get(event_type, ("white", "事件"))
    console.print(Panel(
        f"[bold]{message}[/bold]",
        title=f"[bold {style}]{title}[/bold {style}]",
        border_style=style,
        padding=(0, 2),
    ))
