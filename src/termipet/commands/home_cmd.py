"""家园命令 — home status/upgrade/craft"""
from __future__ import annotations

import sys
import time

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from termipet.database import get_session
from termipet.models.home import Home
from termipet.core.pet_manager import PetManager
from termipet.core.crafting import CraftingManager, RECIPES
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


@click.group("home")
def home_group():
    """家园相关命令"""
    pass


@home_group.command("status")
@safe_cmd
def home_status_cmd():
    """查看家园状态"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        home = session.query(Home).filter_by(pet_id=pet.id).first()
        if home is None:
            print_error("家园数据不存在，请联系开发者。")
            return

        table = Table(
            title=f"🏠 {pet.name} 的家园",
            box=box.ROUNDED,
            border_style="yellow",
            show_header=True,
            header_style="bold yellow",
        )
        table.add_column("房间", style="bold", width=10)
        table.add_column("等级", justify="center", width=6)
        table.add_column("状态", width=20)
        table.add_column("功能", width=25)

        ROOM_INFO = {
            "卧室": ("bedroom_level", "恢复精力、增强睡眠效果"),
            "厨房": ("kitchen_level", "制作食物、药品"),
            "工坊": ("workshop_level", "制作装备、玩具"),
            "花园": ("garden_level", "种植材料"),
            "图书室": ("library_level", "研究技能、制作技能书"),
        }

        for room_name, (attr, func_desc) in ROOM_INFO.items():
            level = getattr(home, attr, 0)
            if level == 0:
                status = "[dim]未解锁[/dim]"
            elif level >= 5:
                status = "[bold magenta]★ MAX ★[/bold magenta]"
            else:
                status = "★" * level + "☆" * (5 - level)

            table.add_row(room_name, str(level) if level > 0 else "—", status, func_desc)

        console.print(table)

        # 装饰分数
        console.print(f"\n[dim]装饰分数：{home.decoration_score:.0f}[/dim]")
        console.print(f"[dim]使用 [bold]pet home upgrade <房间名>[/bold] 升级房间[/dim]")
    finally:
        session.close()


@home_group.command("upgrade")
@click.argument("room")
@safe_cmd
def home_upgrade_cmd(room: str):
    """升级家园房间"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()

        home = session.query(Home).filter_by(pet_id=pet.id).first()
        if home is None:
            print_error("家园数据不存在。")
            return

        # 规范化房间名
        room = room.strip()
        attr = Home.ROOM_KEYS.get(room)
        if attr is None:
            valid = "、".join(Home.ROOM_KEYS.keys())
            raise ValueError(f"未知房间 '{room}'。可用房间：{valid}")

        current_level = getattr(home, attr, 0)
        max_level = 5
        next_level = current_level + 1

        if current_level >= max_level:
            raise ValueError(f"「{room}」已达到最高等级 {max_level}！")

        # 查看升级费用
        cost_table = Home.UPGRADE_COSTS.get(attr, {})
        if next_level not in cost_table:
            raise ValueError(f"没有找到「{room}」等级 {next_level} 的升级配置。")

        coins_cost, materials = cost_table[next_level]

        # 检查金币
        if pet.coins < coins_cost:
            raise ValueError(
                f"金币不足！升级到等级 {next_level} 需要 {coins_cost} 金币，"
                f"当前只有 {pet.coins} 金币。"
            )

        # 检查材料
        from termipet.models.item import Item, Inventory
        missing_mats = {}
        for mat_name, qty in materials.items():
            # 通过名字查找
            item = session.query(Item).filter(Item.name == mat_name).first()
            if item is None:
                # 尝试key
                item = session.query(Item).filter(Item.key == mat_name).first()
            if item is None:
                missing_mats[mat_name] = qty
                continue
            inv = session.query(Inventory).filter_by(pet_id=pet.id, item_id=item.id).first()
            have = inv.quantity if inv else 0
            if have < qty:
                missing_mats[mat_name] = qty - have

        if missing_mats:
            missing_str = "、".join(f"{k}×{v}" for k, v in missing_mats.items())
            raise ValueError(f"材料不足！缺少：{missing_str}")

        # 确认升级
        mats_str = "、".join(f"{k}×{v}" for k, v in materials.items()) if materials else "无需材料"
        try:
            confirmed = click.confirm(
                f"升级「{room}」到 Lv.{next_level} 需要：{coins_cost}金币、{mats_str}，确定吗？",
                default=True
            )
        except click.exceptions.Abort:
            print_info("已取消。")
            return
        if not confirmed:
            print_info("已取消。")
            return

        # 执行升级
        with console.status(f"[yellow]升级「{room}」中……[/yellow]", spinner="dots"):
            time.sleep(1.0)

            # 扣除费用
            pet.coins -= coins_cost
            for mat_name, qty in materials.items():
                item = session.query(Item).filter(
                    (Item.name == mat_name) | (Item.key == mat_name)
                ).first()
                if item:
                    inv = session.query(Inventory).filter_by(pet_id=pet.id, item_id=item.id).first()
                    if inv:
                        inv.quantity -= qty
                        if inv.quantity <= 0:
                            session.delete(inv)

            setattr(home, attr, next_level)
            session.commit()

        console.print(Panel(
            f"[bold]「{room}」成功升级到 Lv.[bold yellow]{next_level}[/bold yellow][/bold]！\n"
            f"[dim]消耗：{coins_cost}金币  剩余金币：{pet.coins}[/dim]",
            title="🏗️ 升级成功！",
            border_style="yellow",
            padding=(0, 2),
        ))
    finally:
        session.close()


@home_group.command("craft")
@click.argument("recipe")
@safe_cmd
def home_craft_cmd(recipe: str):
    """制作物品"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        cm = CraftingManager(session)

        with console.status(f"[cyan]正在制作「{recipe}」……[/cyan]", spinner="dots"):
            time.sleep(1.2)
            result = cm.craft(pet, recipe)

        console.print(Panel(
            f"成功制作「[bold cyan]{result['recipe']}[/bold cyan]」\n"
            f"获得：[bold yellow]{result['output']}[/bold yellow] × {result['qty']}",
            title="🔨 制作成功！",
            border_style="cyan",
            padding=(0, 2),
        ))
    finally:
        session.close()


@home_group.command("recipes")
@safe_cmd
def home_recipes_cmd():
    """查看可用配方"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        cm = CraftingManager(session)

        available = cm.list_available_recipes(pet)

        if not available:
            print_info("当前没有可用配方。升级厨房、工坊或图书室来解锁更多配方。")
            return

        table = Table(
            title="📜 可用配方",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold cyan",
        )
        table.add_column("配方名", style="bold", width=12)
        table.add_column("所需材料", width=30)
        table.add_column("产出", width=15)
        table.add_column("可制作", justify="center", width=8)

        for r in available:
            # 将材料 key 翻译成名称
            mats_display = []
            for mat_key, qty in r["materials"].items():
                from termipet.models.item import Item as ItemModel
                mat_item = session.query(ItemModel).filter_by(key=mat_key).first()
                mat_name = mat_item.name if mat_item else mat_key
                mats_display.append(f"{mat_name}×{qty}")
            mats_str = "  ".join(mats_display)
            can = "[green]✓[/green]" if r["can_craft"] else "[red]✗[/red]"
            if r["missing"]:
                # 翻译缺少材料名
                missing_parts = []
                for mk, mv in r["missing"].items():
                    from termipet.models.item import Item as ItemModel
                    mi = session.query(ItemModel).filter_by(key=mk).first()
                    mn = mi.name if mi else mk
                    missing_parts.append(f"(-{mn}×{mv})")
                can += f" [dim red]{' '.join(missing_parts)}[/dim red]"

            # 产出名称
            from termipet.models.item import Item as ItemModel
            out_item = session.query(ItemModel).filter_by(key=r["output"]).first()
            out_name = out_item.name if out_item else r["output"]

            table.add_row(r["name"], mats_str, f"{out_name}×{r['qty']}", can)

        console.print(table)
        console.print(f"[dim]使用 [bold]pet home craft <配方名>[/bold] 制作物品[/dim]")
    finally:
        session.close()
