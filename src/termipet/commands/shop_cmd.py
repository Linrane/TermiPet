"""商店命令 — shop list/buy/sell/inventory/equip"""
from __future__ import annotations

import sys

import click
from rich.table import Table
from rich.panel import Panel
from rich import box

from termipet.database import get_session
from termipet.core.economy import EconomyManager
from termipet.core.pet_manager import PetManager
from termipet.display.status_panel import (
    print_success, print_error, print_warning, print_info, console
)

RARITY_COLORS = {"普通": "white", "稀有": "cyan", "传说": "bright_magenta"}
TYPE_NAMES = {"consumable": "食物/药品", "material": "材料", "equipment": "装备", "collectible": "收藏品"}


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


@click.group("shop")
def shop_group():
    """商店相关命令"""
    pass


@shop_group.command("list")
@click.option("--category", "-c", default=None, help="分类筛选：食物/材料/装备/收藏")
@safe_cmd
def shop_list_cmd(category: str | None):
    """查看商店商品"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        em = EconomyManager(session)

        items = em.list_shop_items(category)
        if not items:
            print_info("暂无商品" + (f"（分类：{category}）" if category else "") + "。")
            return

        table = Table(
            title=f"🛒 灵界商店  [bold yellow]{pet.coins} 金币 · {pet.stardust} 星尘[/bold yellow]",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold cyan",
        )
        table.add_column("物品名", style="bold", width=14)
        table.add_column("分类", width=10)
        table.add_column("品质", width=8)
        table.add_column("价格", justify="right", width=8)
        table.add_column("出售价", justify="right", width=8)
        table.add_column("效果", width=28)

        for item in items:
            rarity_color = RARITY_COLORS.get(item.rarity, "white")
            effects = item.effects
            effects_str = "  ".join(f"{k}+{v}" for k, v in effects.items() if isinstance(v, (int, float)) and v > 0)
            can_afford = "[green]" if pet.coins >= item.buy_price else "[red]"

            table.add_row(
                item.name,
                TYPE_NAMES.get(item.item_type, item.item_type),
                f"[{rarity_color}]{item.rarity}[/{rarity_color}]",
                f"{can_afford}{item.buy_price}🪙[/{'green' if pet.coins >= item.buy_price else 'red'}]",
                f"{item.sell_price}🪙",
                effects_str or "[dim]—[/dim]",
            )

        console.print(table)
        console.print(f"[dim]使用 [bold]pet shop buy <物品名>[/bold] 购买，[bold]pet shop sell <物品名>[/bold] 出售[/dim]")
    finally:
        session.close()


@shop_group.command("buy")
@click.argument("item")
@click.option("--count", "-c", default=1, type=int, help="购买数量")
@safe_cmd
def shop_buy_cmd(item: str, count: int):
    """购买物品"""
    count = max(1, count)
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        em = EconomyManager(session)

        result = em.buy(pet, item, count)

        console.print(Panel(
            f"购买了 [bold cyan]{result['item']}[/bold cyan] × {result['count']}\n"
            f"花费 [bold red]{result['cost']}[/bold red] 金币  剩余 [bold yellow]{result['remaining_coins']}[/bold yellow] 金币",
            title="✅ 购买成功",
            border_style="green",
            padding=(0, 2),
        ))
    finally:
        session.close()


@shop_group.command("sell")
@click.argument("item")
@click.option("--count", "-c", default=1, type=int, help="出售数量")
@safe_cmd
def shop_sell_cmd(item: str, count: int):
    """出售物品"""
    count = max(1, count)
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        em = EconomyManager(session)

        result = em.sell(pet, item, count)

        console.print(Panel(
            f"出售了 [bold cyan]{result['item']}[/bold cyan] × {result['count']}\n"
            f"获得 [bold green]{result['earned']}[/bold green] 金币  当前 [bold yellow]{result['coins']}[/bold yellow] 金币",
            title="💰 出售成功",
            border_style="yellow",
            padding=(0, 2),
        ))
    finally:
        session.close()


@shop_group.command("inventory")
@safe_cmd
def inventory_cmd():
    """查看背包"""
    session = get_session()
    try:
        pm = PetManager(session)
        pet = pm.require_active_pet()
        em = EconomyManager(session)

        inv_list = em.get_inventory(pet)
        if not inv_list:
            print_info("背包是空的！")
            return

        table = Table(
            title=f"🎒 {pet.name} 的背包",
            box=box.ROUNDED,
            border_style="yellow",
            header_style="bold yellow",
        )
        table.add_column("物品名", style="bold", width=14)
        table.add_column("数量", justify="center", width=6)
        table.add_column("分类", width=10)
        table.add_column("品质", width=8)
        table.add_column("装备", justify="center", width=6)

        for inv in inv_list:
            item = inv.item
            rarity_color = RARITY_COLORS.get(item.rarity, "white")
            equipped_str = "[bold green]✓[/bold green]" if inv.equipped else ""
            table.add_row(
                item.name,
                str(inv.quantity),
                TYPE_NAMES.get(item.item_type, item.item_type),
                f"[{rarity_color}]{item.rarity}[/{rarity_color}]",
                equipped_str,
            )

        console.print(table)
    finally:
        session.close()
