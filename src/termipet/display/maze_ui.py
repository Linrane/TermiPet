"""迷宫 UI — ASCII 迷宫渲染"""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from termipet.models.maze import (
    MazeState,
    CELL_WALL, CELL_FLOOR, CELL_START, CELL_EXIT,
    CELL_CHEST, CELL_TRAP, CELL_ENEMY, CELL_PUZZLE, CELL_SHOP, CELL_STORY,
)
from termipet.display.themes import t

console = Console()

# 视野半径（默认2格，狗型技能可扩展）
DEFAULT_VIEW_RADIUS = 2

# 单元格渲染表
CELL_RENDER = {
    CELL_WALL:   ("[dim]▓[/dim]",   "dim"),
    CELL_FLOOR:  ("·",              "dim"),
    CELL_START:  ("[green]S[/green]", "green"),
    CELL_EXIT:   ("[bright_yellow]E[/bright_yellow]", "bright_yellow"),
    CELL_CHEST:  ("[yellow]C[/yellow]", "yellow"),
    CELL_TRAP:   ("[red]T[/red]",   "red"),
    CELL_ENEMY:  ("[bright_red]M[/bright_red]", "bright_red"),
    CELL_PUZZLE: ("[magenta]?[/magenta]", "magenta"),
    CELL_SHOP:   ("[cyan]$[/cyan]", "cyan"),
    CELL_STORY:  ("[bright_magenta]![/bright_magenta]", "bright_magenta"),
}

PLAYER_CHAR = "[bold bright_cyan]@[/bold bright_cyan]"


def render_maze(state: MazeState, view_radius: int = DEFAULT_VIEW_RADIUS) -> str:
    """渲染迷宫视野区域，返回 rich markup 字符串"""
    maze_map = state.maze_map
    if not maze_map:
        return "[dim]迷宫数据为空[/dim]"

    explored = state.explored
    px, py = state.pos_x, state.pos_y
    h = len(maze_map)
    w = len(maze_map[0]) if h > 0 else 0

    lines = []

    for y in range(h):
        row_chars = []
        for x in range(w):
            dist = abs(x - px) + abs(y - py)   # 曼哈顿距离
            is_visible = dist <= view_radius
            is_explored = (x, y) in explored
            is_player = (x == px and y == py)

            if is_player:
                row_chars.append(PLAYER_CHAR)
            elif is_visible:
                cell = maze_map[y][x]
                rendered, _ = CELL_RENDER.get(cell, (cell, "white"))
                row_chars.append(rendered)
            elif is_explored:
                cell = maze_map[y][x]
                if cell == CELL_WALL:
                    row_chars.append("[dim]▓[/dim]")
                else:
                    row_chars.append("[dim]·[/dim]")
            else:
                row_chars.append("[dim on black] [/dim on black]")

        lines.append(" ".join(row_chars))

    return "\n".join(lines)


def print_maze(state: MazeState, view_radius: int = DEFAULT_VIEW_RADIUS,
               pet_name: str = "灵兽", event_msg: str = "") -> None:
    """打印完整迷宫面板"""
    maze_str = render_maze(state, view_radius)

    # 图例
    legend = (
        f"[green]S[/green]=起点 [bright_yellow]E[/bright_yellow]=出口 "
        f"[yellow]C[/yellow]=宝箱 [red]T[/red]=陷阱 "
        f"[bright_red]M[/bright_red]=怪物 [magenta]?[/magenta]=谜题 "
        f"[cyan]$[/cyan]=商店  "
        f"[bold bright_cyan]@[/bold bright_cyan]={pet_name}"
    )

    content = maze_str
    if event_msg:
        content += f"\n\n[bold]{event_msg}[/bold]"
    content += f"\n[dim]{legend}[/dim]"

    title = (
        f"[bold cyan]迷宫 — 第 {state.floor} 层[/bold cyan]  "
        f"位置({state.pos_x},{state.pos_y})"
    )

    console.print(Panel(
        content,
        title=title,
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    ))


def print_battle_animation(pet_choice: str, enemy_choice: str, result: str) -> None:
    """战斗动画"""
    import time

    CHOICE_EMOJI = {"攻击": "⚔️", "防御": "🛡️", "技能": "✨"}
    RESULT_COLOR = {"胜利": "green", "失败": "red", "平局": "yellow", "defeated": "red"}

    pet_e = CHOICE_EMOJI.get(pet_choice, "❓")
    enemy_e = CHOICE_EMOJI.get(enemy_choice, "👾")
    color = RESULT_COLOR.get(result, "white")

    frames = [
        f"  {pet_e}  VS  {enemy_e}  ",
        f"  {pet_e} ~~~ {enemy_e}  ",
        f"  {pet_e} === {enemy_e}  ",
        f"  [{color}]{result}！[/{color}]  {pet_e} vs {enemy_e}  ",
    ]

    for frame in frames:
        console.print(f"\r{frame}", end="")
        time.sleep(0.25)
    console.print()


def print_loot_animation(items: list[str]) -> None:
    """战利品获取动画"""
    import time
    if not items:
        return
    console.print("[yellow]✨ 获得战利品：[/yellow]", end="")
    for item in items:
        time.sleep(0.15)
        console.print(f" [bold]{item}[/bold]", end="")
    console.print()
