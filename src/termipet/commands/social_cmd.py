"""任务/成就/收集/故事命令"""
from __future__ import annotations

import sys

import click
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from termipet.database import get_session
from termipet.core.pet_manager import PetManager
from termipet.core.quests import QuestManager
from termipet.models.story import StoryFragment, STORY_FRAGMENTS
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


@click.command("quests")
@click.option("--claim", "-c", default=None, help="领取指定任务奖励（任务key）")
@safe_cmd
def quests_cmd(claim: str | None):
    """查看任务列表"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        qm = QuestManager(session)

        if claim:
            result = qm.claim_quest(pet, claim)
            session.commit()
            console.print(Panel(
                f"领取任务「{result['name']}」奖励！\n"
                f"[bold yellow]+{result['coins']} 金币[/bold yellow]  "
                f"[bold cyan]+{result['stardust']} 星尘[/bold cyan]",
                title="🎁 奖励已领取",
                border_style="yellow",
                padding=(0, 2),
            ))
            return

        quests = qm.get_quests(pet)
        if not quests:
            print_info("暂无任务数据。")
            return

        # 分日常/周常显示
        daily = [q for q in quests if q.definition.get("type") == "daily"]
        weekly = [q for q in quests if q.definition.get("type") == "weekly"]

        def build_quest_table(title: str, quest_list) -> Table:
            t = Table(title=title, box=box.ROUNDED, border_style="cyan", header_style="bold cyan")
            t.add_column("任务名", style="bold", width=14)
            t.add_column("说明", width=24)
            t.add_column("进度", justify="center", width=10)
            t.add_column("奖励", width=14)
            t.add_column("状态", justify="center", width=10)

            for q in quest_list:
                defn = q.definition
                target = defn.get("target", 1)
                progress_str = f"{q.progress}/{target}"
                reward_str = f"{defn.get('coins',0)}🪙 {defn.get('stardust',0)}✨"

                if q.claimed:
                    status = "[dim]已领取[/dim]"
                elif q.completed:
                    status = "[bold green]可领取！[/bold green]"
                else:
                    pct = q.progress / target
                    bar = "█" * int(pct * 8) + "░" * (8 - int(pct * 8))
                    color = "green" if pct >= 0.8 else "yellow" if pct >= 0.5 else "red"
                    status = f"[{color}]{bar}[/{color}]"

                t.add_row(
                    defn.get("name", q.quest_key),
                    defn.get("desc", ""),
                    progress_str,
                    reward_str,
                    status,
                )
            return t

        if daily:
            console.print(build_quest_table("📅 日常任务", daily))
        if weekly:
            console.print()
            console.print(build_quest_table("📆 周常任务", weekly))

        # 有可领取的提示
        claimable = [q for q in quests if q.completed and not q.claimed]
        if claimable:
            console.print(f"\n[bold green]有 {len(claimable)} 个任务可以领取奖励！[/bold green]")
            console.print("[dim]使用 [bold]pet quests --claim <任务key>[/bold] 领取[/dim]")
    finally:
        session.close()


@click.command("achievements")
@safe_cmd
def achievements_cmd():
    """查看成就"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        qm = QuestManager(session)

        achievements = qm.get_achievements(pet)

        unlocked = [a for a in achievements if a.unlocked]
        locked = [a for a in achievements if not a.unlocked]

        table = Table(
            title=f"🏆 成就  已解锁 {len(unlocked)}/{len(achievements)}",
            box=box.ROUNDED,
            border_style="yellow",
            header_style="bold yellow",
        )
        table.add_column("成就名", style="bold", width=14)
        table.add_column("类型", width=8)
        table.add_column("说明", width=28)
        table.add_column("进度", justify="center", width=10)
        table.add_column("奖励", width=8)

        # 先显示已解锁
        for a in unlocked:
            defn = a.definition
            if defn.get("hidden") and not a.unlocked:
                continue
            table.add_row(
                f"[bold yellow]{defn.get('name', a.achievement_key)}[/bold yellow]",
                defn.get("type", ""),
                defn.get("desc", ""),
                "[bold green]✓ 已解锁[/bold green]",
                f"[cyan]{defn.get('stardust', 0)}✨[/cyan]",
            )

        # 再显示未解锁
        for a in locked:
            defn = a.definition
            is_hidden = defn.get("hidden", False)
            target = defn.get("target", 1)
            progress_pct = a.progress / target if target > 0 else 0
            bar = "█" * int(progress_pct * 6) + "░" * (6 - int(progress_pct * 6))

            table.add_row(
                f"[dim]{'???' if is_hidden else defn.get('name', a.achievement_key)}[/dim]",
                defn.get("type", "") if not is_hidden else "???",
                "[dim italic]???[/dim italic]" if is_hidden else f"[dim]{defn.get('desc', '')}[/dim]",
                f"[dim]{bar}[/dim] {a.progress:.0f}/{target}",
                f"[dim]{defn.get('stardust', 0)}✨[/dim]",
            )

        console.print(table)
    finally:
        session.close()


@click.command("story")
@click.option("--read", "-r", default=None, help="阅读指定碎片（序号）")
@safe_cmd
def story_cmd(read: str | None):
    """查看故事碎片"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        fragments = (
            session.query(StoryFragment)
            .filter_by(pet_id=pet.id)
            .all()
        )
        fragments.sort(key=lambda f: STORY_FRAGMENTS.get(f.fragment_key, {}).get("order", 99))

        if not fragments:
            print_info("还没有解锁任何故事碎片。\n通过探险、成长来解锁更多故事……")
            return

        if read is not None:
            # 阅读特定碎片
            try:
                idx = int(read) - 1
                frag = fragments[idx]
            except (ValueError, IndexError):
                raise ValueError(f"无效的碎片序号 '{read}'，请输入 1 到 {len(fragments)} 之间的数字。")

            defn = frag.definition
            frag.read = True
            session.commit()

            console.print()
            console.print(Panel(
                f"[italic]{defn.get('content', '???')}[/italic]",
                title=f"[bold magenta]📖 {defn.get('title', '???')}[/bold magenta]",
                border_style="magenta",
                box=box.DOUBLE,
                padding=(1, 3),
            ))
            return

        # 列出所有碎片
        table = Table(
            title=f"📚 故事碎片  已解锁 {len(fragments)}/{len(STORY_FRAGMENTS)}",
            box=box.ROUNDED,
            border_style="magenta",
            header_style="bold magenta",
        )
        table.add_column("序号", justify="center", width=4)
        table.add_column("标题", width=16)
        table.add_column("状态", justify="center", width=8)

        for i, frag in enumerate(fragments, 1):
            defn = frag.definition
            status = "[dim]已读[/dim]" if frag.read else "[bold bright_magenta]★ 新[/bold bright_magenta]"
            table.add_row(str(i), defn.get("title", "???"), status)

        console.print(table)
        console.print(f"[dim]使用 [bold]pet story --read <序号>[/bold] 阅读故事碎片[/dim]")
    finally:
        session.close()


@click.command("collection")
@safe_cmd
def collection_cmd():
    """查看收藏品博物架"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        qm = QuestManager(session)

        achievements = [a for a in qm.get_achievements(pet) if a.unlocked]

        console.print()
        console.print(Panel(
            f"[bold cyan]✦ {pet.name} 的博物架 ✦[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE,
        ))

        if not achievements:
            console.print("[dim]    博物架空空如也……完成成就来收集徽章吧！[/dim]")
        else:
            # 网格展示成就徽章
            badges = []
            for a in achievements:
                defn = a.definition
                badges.append(f"[bold yellow]【{defn.get('name', '???')}】[/bold yellow]")

            # 每行4个
            for i in range(0, len(badges), 4):
                row = "   ".join(badges[i:i+4])
                console.print(f"  {row}")

        console.print()
        console.print(f"  [dim]已解锁成就：{len(achievements)} 个[/dim]")
        console.print(f"  [dim]故事碎片：{session.query(StoryFragment).filter_by(pet_id=pet.id).count()} 片[/dim]")
    finally:
        session.close()
