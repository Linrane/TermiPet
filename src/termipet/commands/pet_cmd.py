"""宠物基础命令 — adopt, status, feed, play, clean, sleep, train, skill"""
from __future__ import annotations

import sys
import time

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from termipet.database import get_session
from termipet.models.pet import Pet, Species
from termipet.core.pet_manager import PetManager
from termipet.core.skill_system import SkillSystem
from termipet.core.events import EventManager
from termipet.display.status_panel import (
    build_status_panel, live_status,
    print_success, print_error, print_warning, print_info, print_event_box, console
)

# ── 通用错误处理装饰器 ─────────────────────────────────────────────────────────
def safe_cmd(func):
    """包裹命令，统一捕获异常，避免用户看到 traceback"""
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


# ══════════════════════════════════════════════════════════════════════════════
#  adopt
# ══════════════════════════════════════════════════════════════════════════════
@click.command("adopt")
@click.argument("species")
@click.option("--name", "-n", default="", help="宠物名字")
@safe_cmd
def adopt_cmd(species: str, name: str):
    """领养一只新灵兽"""
    session = get_session()
    try:
        pm = PetManager(session)

        # 如果没提供名字，交互式询问
        if not name:
            name = click.prompt("请给你的灵兽取个名字", default="小灵")

        # 检查是否已有宠物
        existing = pm.get_active_pet()
        if existing:
            try:
                confirmed = click.confirm(
                    f"你已有宠物「{existing.name}」，领养新宠物会将其设为非活跃状态，确定吗？",
                    default=False
                )
            except click.exceptions.Abort:
                print_info("已取消。")
                return
            if not confirmed:
                print_info("已取消。")
                return

        with console.status(f"[cyan]正在召唤 {species} 灵兽……[/cyan]", spinner="dots"):
            time.sleep(1.2)
            pet = pm.adopt(species_key=species.lower(), name=name)

        console.print()
        console.print(Panel(
            f"[bold cyan]恭喜！你领养了一只 {_species_name(species)} 灵兽！[/bold cyan]\n"
            f"名字：[bold yellow]{pet.name}[/bold yellow]\n"
            f"性格：{pet.personality}  天赋：[italic]{pet.talent}[/italic]\n\n"
            f"[dim]它目前还是一颗蛋，请耐心等待孵化……[/dim]\n"
            f"[dim]使用 [bold]pet status[/bold] 查看状态，[bold]pet feed[/bold] 喂食。[/dim]",
            title="✨ 领养成功 ✨",
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2),
        ))
    finally:
        session.close()


def _species_name(key: str) -> str:
    names = {"cat": "猫型", "dog": "犬型", "bird": "鸟型", "mech": "机械型", "mystery": "神秘型"}
    return names.get(key.lower(), key)


# ══════════════════════════════════════════════════════════════════════════════
#  status
# ══════════════════════════════════════════════════════════════════════════════
@click.command("status")
@click.option("--live", is_flag=True, help="动态刷新状态（30秒）")
@safe_cmd
def status_cmd(live: bool):
    """查看宠物当前状态"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        pm.apply_decay(pet)
        session.commit()

        if live:
            live_status(pet, duration=30)
        else:
            panel = build_status_panel(pet)
            console.print(panel)

            # 随机事件检查
            em = EventManager(session)
            event = em.maybe_trigger(pet, base_chance=0.1)
            if event:
                console.print()
                print_event_box(f"💫 {event['title']}", event['desc'], style="yellow")
                session.commit()
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  feed
# ══════════════════════════════════════════════════════════════════════════════
@click.command("feed")
@click.option("--item", "-i", default=None, help="指定食物名称或 key")
@safe_cmd
def feed_cmd(item: str | None):
    """喂食宠物"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        # 动画
        with console.status(f"[cyan]正在喂食 {pet.name}……[/cyan]", spinner="hearts"):
            time.sleep(0.8)
            result = pm.feed(pet, item_key=item)

        item_name = result.get("item", "食物")
        effects = result.get("effects", {})
        STAT_ZH = {
            "hunger": "饱腹", "happiness": "快乐", "cleanliness": "清洁",
            "health": "健康", "energy": "精力", "intelligence": "智力",
            "bond": "亲密", "constitution": "体质",
        }
        effects_str = "  ".join(
            f"[green]+{v:.0f}[/green] {STAT_ZH.get(k, k)}"
            for k, v in effects.items() if isinstance(v, (int, float)) and v > 0
        )

        console.print(Panel(
            f"[bold]喂食了「{item_name}」[/bold]\n{effects_str or '普通饲料喂食完成'}",
            title=f"🍖 {pet.name} 吃得很开心！",
            border_style="green",
            padding=(0, 2),
        ))

        # 低健康警告
        if pet.health < 20:
            print_warning(f"{pet.name} 健康值很低（{pet.health:.0f}），请尽快使用药品！")

        # 随机事件
        em = EventManager(session)
        event = em.maybe_trigger(pet)
        if event:
            console.print()
            print_event_box(f"✨ {event['title']}", event['desc'], style="yellow")
            session.commit()
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  play
# ══════════════════════════════════════════════════════════════════════════════
@click.command("play")
@safe_cmd
def play_cmd():
    """和宠物玩耍"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        with console.status(f"[cyan]和 {pet.name} 玩耍中……[/cyan]", spinner="hearts"):
            time.sleep(1.0)
            result = pm.play(pet)

        console.print(Panel(
            f"[bold yellow]快乐值 +{result['happiness_gain']:.0f}[/bold yellow]  "
            f"[bold cyan]亲密度 +{result['bond_gain']:.1f}[/bold cyan]  "
            f"[dim]精力 -{result['energy_cost']:.0f}[/dim]",
            title=f"🎮 {pet.name} 玩得很开心！",
            border_style="yellow",
            padding=(0, 2),
        ))

        em = EventManager(session)
        event = em.maybe_trigger(pet)
        if event:
            console.print()
            print_event_box(f"✨ {event['title']}", event['desc'], style="yellow")
            session.commit()
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  clean
# ══════════════════════════════════════════════════════════════════════════════
@click.command("clean")
@safe_cmd
def clean_cmd():
    """清洁宠物"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        with console.status(f"[cyan]正在给 {pet.name} 洗澡……[/cyan]", spinner="line"):
            time.sleep(0.8)
            result = pm.clean(pet)

        console.print(Panel(
            f"[bold cyan]清洁度 +{result['cleanliness_gain']:.0f}[/bold cyan]  "
            f"[bold yellow]快乐值 +{result['happiness_gain']:.0f}[/bold yellow]",
            title=f"🛁 {pet.name} 干净清爽！",
            border_style="cyan",
            padding=(0, 2),
        ))
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  sleep
# ══════════════════════════════════════════════════════════════════════════════
@click.command("sleep")
@click.argument("hours", type=float, default=4.0)
@safe_cmd
def sleep_cmd(hours: float):
    """让宠物休息（默认4小时），范围 0.5-12 小时"""
    if hours <= 0:
        print_error("休息时间必须大于 0 小时。")
        return
    if hours > 12:
        print_warning("最长休息时间为 12 小时，已自动调整。")
        hours = 12.0

    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        with console.status(f"[cyan]{pet.name} 进入梦乡……（{hours:.1f}小时）[/cyan]", spinner="moon"):
            time.sleep(1.0)
            result = pm.sleep(pet, hours)

        console.print(Panel(
            f"[bold cyan]精力 +{result['energy_gain']:.0f}[/bold cyan]  "
            f"[bold green]健康 +{result['health_gain']:.0f}[/bold green]",
            title=f"💤 {pet.name} 睡了 {hours:.1f} 小时，精神满满！",
            border_style="blue",
            padding=(0, 2),
        ))
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  train
# ══════════════════════════════════════════════════════════════════════════════
@click.command("train")
@click.argument("skill_name")
@safe_cmd
def train_cmd(skill_name: str):
    """训练/学习技能"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        ss = SkillSystem(session)

        pm.apply_decay(pet)

        with console.status(f"[cyan]{pet.name} 正在努力训练「{skill_name}」……[/cyan]", spinner="star"):
            time.sleep(1.0)
            result = ss.learn_skill(pet, skill_name)

        action = result['action']
        console.print(Panel(
            f"[bold]{action}技能[/bold]「[bold cyan]{result['skill']}[/bold cyan]」"
            f"Lv.{result['level']}  消耗 {result['cost']} 技能点\n"
            f"[dim]剩余技能点：{pet.skill_points}[/dim]",
            title=f"⚡ 技能{action}成功！",
            border_style="bright_cyan",
            padding=(0, 2),
        ))
    finally:
        session.close()


# ══════════════════════════════════════════════════════════════════════════════
#  skill list
# ══════════════════════════════════════════════════════════════════════════════
@click.group("skill")
def skill_group():
    """技能相关命令"""
    pass


@skill_group.command("list")
@safe_cmd
def skill_list_cmd():
    """查看技能树"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        ss = SkillSystem(session)

        skills = ss.get_available_skills(pet)

        table = Table(
            title=f"✦ {pet.name} 的技能树 （技能点：{pet.skill_points}）",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("技能名", style="bold", width=10)
        table.add_column("类型", width=8)
        table.add_column("费用", justify="center", width=6)
        table.add_column("等级", justify="center", width=6)
        table.add_column("说明", width=30)
        table.add_column("状态", justify="center", width=8)

        for s in skills:
            status = f"[green]Lv.{s['level']}[/green]" if s["learned"] else "[dim]未学习[/dim]"
            cost_str = f"[yellow]{s['cost']}[/yellow]" if s["cost"] <= pet.skill_points else f"[red]{s['cost']}[/red]"
            table.add_row(
                s["name"],
                s["type"],
                cost_str,
                str(s["level"]) if s["learned"] else "-",
                s["desc"],
                status,
            )

        console.print(table)
        console.print(f"[dim]使用 [bold]pet train <技能名>[/bold] 学习技能[/dim]")
    finally:
        session.close()
