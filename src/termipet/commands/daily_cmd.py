"""日常事件命令 — pet daily"""
from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from termipet.database import get_session
from termipet.core.pet_manager import PetManager
from termipet.core.daily_events import DailyEventSystem
from termipet.display.status_panel import (
    print_success, print_error, print_info, console
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


@click.group("daily")
def daily_group():
    """日常事件 — 查看宠物在你离开期间都做了什么"""
    pass


@daily_group.command(name="view")
@click.option("--all", "show_all", is_flag=True, help="显示所有历史事件（而非仅未读）")
@safe_cmd
def daily_view_cmd(show_all: bool):
    """查看日常事件报告"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        # 先检查并生成离线事件
        des = DailyEventSystem(session)
        new_events = des.check_and_generate(pet)
        if new_events:
            pm.apply_decay(pet)
            session.commit()

        # 获取事件列表
        if show_all:
            events = des.get_all_events(pet)
        else:
            events = des.get_unread_events(pet)

        if not events:
            if show_all:
                print_info("还没有任何日常事件记录。离开一段时间后，宠物会有自主行动哦！")
            else:
                print_info("暂无未读日常事件。使用 [bold]pet daily --all[/] 查看历史记录。")
            return

        # 检查未读数量
        unread_count = sum(1 for e in events if not e.read) if show_all else len(events)

        title = f"📖 {pet.name} 的日常事件"
        if not show_all and unread_count > 0:
            title += f"（{unread_count} 条未读）"

        table = Table(
            title=title,
            box=box.ROUNDED,
            border_style="cyan",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("#", justify="center", width=4)
        table.add_column("时间", width=16)
        table.add_column("类别", width=8)
        table.add_column("标题", style="bold", width=18)
        table.add_column("摘要", width=32)
        table.add_column("状态", justify="center", width=6)

        CATEGORY_STYLES = {
            "外出探索": "green",
            "家园日常": "yellow",
            "社交互动": "magenta",
            "天气事件": "blue",
            "成长事件": "cyan",
            "物种特色": "bright_magenta",
        }

        for i, ev in enumerate(events, 1):
            time_str = ev.occurred_at.strftime("%m-%d %H:%M") if ev.occurred_at else "—"
            cat_style = CATEGORY_STYLES.get(ev.category, "white")
            status = "[green]新[/green]" if not ev.read else "[dim]已读[/dim]"

            table.add_row(
                str(i),
                time_str,
                f"[{cat_style}]{ev.category}[/{cat_style}]",
                ev.title,
                ev.summary[:30] + "..." if len(ev.summary) > 30 else ev.summary,
                status,
            )

        console.print(table)
        console.print(
            f"[dim]使用 [bold]pet daily read <序号>[/bold] 查看详情  "
            f"[bold]pet daily clear[/bold] 标记全部已读[/dim]"
        )
    finally:
        session.close()


@daily_group.command("read")
@click.argument("index", type=int, required=True)
@safe_cmd
def daily_read_cmd(index: int):
    """阅读具体事件详情"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        des = DailyEventSystem(session)
        events = des.get_all_events(pet)

        if index < 1 or index > len(events):
            total = len(events)
            raise ValueError(
                f"无效序号 {index}。当前共有 {total} 条事件记录，"
                f"请输入 1-{total} 之间的数字。"
            )

        ev = events[index - 1]

        # 标记已读
        des.mark_read(pet, ev.id)

        # 显示详情
        result = ev.result
        result_parts = []
        STAT_ZH = {
            "hunger": "饱腹", "happiness": "快乐", "cleanliness": "清洁",
            "health": "健康", "energy": "精力", "intelligence": "智力",
            "bond": "亲密", "constitution": "体质",
        }
        for k, v in result.items():
            if k in STAT_ZH:
                if v >= 0:
                    result_parts.append(f"[green]+{v:.0f}[/green] {STAT_ZH[k]}")
                else:
                    result_parts.append(f"[red]{v:.0f}[/red] {STAT_ZH[k]}")
            elif k == "coins":
                if v >= 0:
                    result_parts.append(f"[yellow]+{v}[/yellow] 金币")
                else:
                    result_parts.append(f"[yellow]{v}[/yellow] 金币")
            elif k == "stardust":
                result_parts.append(f"[magenta]+{v}[/magenta] 星尘")
            elif k == "item":
                result_parts.append(f"[cyan]获得 {v}[/cyan]")

        result_str = "  ".join(result_parts) if result_parts else "无属性变化"

        time_str = ev.occurred_at.strftime("%Y-%m-%d %H:%M") if ev.occurred_at else "未知时间"

        console.print(Panel(
            f"[bold]{ev.title}[/bold]\n"
            f"[dim]类别：{ev.category}  时间：{time_str}[/dim]\n\n"
            f"{ev.detail}\n\n"
            f"[bold]效果：[/bold]{result_str}",
            title=f"📖 事件详情 #{index}",
            border_style="cyan",
            padding=(1, 2),
        ))
    finally:
        session.close()


@daily_group.command("clear")
@safe_cmd
def daily_clear_cmd():
    """标记所有日常事件为已读"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        des = DailyEventSystem(session)
        count = des.mark_all_read(pet)

        if count > 0:
            print_success(f"已将 {count} 条日常事件标记为已读。")
        else:
            print_info("没有未读的日常事件。")
    finally:
        session.close()
