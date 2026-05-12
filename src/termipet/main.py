"""TermiPet 2.2 — CLI main entry"""
from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from termipet.locale import t, set_locale, get_lang

console = Console()

# Initialize locale at module level (before CLI docs are computed)
try:
    set_locale()
except Exception:
    pass


# ── Global startup init ─────────────────────────────────────────────────────
def _startup_init() -> None:
    """Initialize database and seed data"""
    try:
        from termipet.utils.seeds import initialize_game
        initialize_game()
    except Exception as e:
        console.print(f"[yellow]{t('cli.init_warning', error=str(e))}[/yellow]")


# ── Banner ─────────────────────────────────────────────────────────────────
BANNER = r"""
  ______  _________  ______  __  __  _____  ____   _____  ______
 /_  __/ / _____  / / ___  |/  |/  |/_  _/ / __ \ / __  |/_  __/
  / /   / /____/ / / /__/ // /|_/ /  / /  / /_/ // //_/  / /
 /_/   /_______/  \____/ /_/    /_/  /_/  / .___//_/     /_/
                                         /_/
"""


def print_banner():
    console.print(Panel(
        f"[bold cyan]{t('banner.title')}[/bold cyan]\n"
        f"[dim]{t('banner.subtitle')}[/dim]",
        border_style="cyan",
        box=box.DOUBLE,
        padding=(0, 2),
    ))


# ═════════════════════════════════════════════════════════════════════════════
#  Main command group
# ═════════════════════════════════════════════════════════════════════════════
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--lang", default=None, help="Language: zh / en")
@click.pass_context
def cli(ctx, lang: str | None):
    """
    TermiPet 2.2 — Terminal Spirit Companion

    \b
    {quick_start}
      {adopt_example}
      {status_example}
      {feed_example}
      {play_example}
      {adventure_example}

    {help_hint}
    """.format(
        quick_start=t("cli.quick_start"),
        adopt_example=t("cli.adopt_example"),
        status_example=t("cli.status_example"),
        feed_example=t("cli.feed_example"),
        play_example=t("cli.play_example"),
        adventure_example=t("cli.adventure_example"),
        help_hint=t("cli.help_hint"),
    )
    if lang:
        from termipet.locale import set_locale
        set_locale(lang)

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
        from termipet.commands.daily_cmd import daily_group

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
        cli.add_command(daily_group,     "daily")

    except ImportError as e:
        console.print(f"[red]{t('cli.cmd_load_fail', error=str(e))}[/red]")
        sys.exit(1)


_register_commands()


# ── Convenience commands ────────────────────────────────────────────────────
@cli.command("info")
def info_cmd():
    """Show game info and help"""
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
            console.print(f"[dim]{t('common.no_pet_adopt', cmd='pet adopt <species>')}[/dim]")
            console.print(f"[dim]{t('common.available_species')}[/dim]")
    finally:
        session.close()


@cli.command("list-pets")
def list_pets_cmd():
    """List all adopted pets"""
    from termipet.database import get_session
    from termipet.models.pet import Pet
    from rich.table import Table

    session = get_session()
    try:
        pets = session.query(Pet).all()
        if not pets:
            console.print(f"[dim]{t('common.no_pets')}[/dim]")
            return

        table = Table(
            title=t("common.adopted_pets"),
            box=box.ROUNDED, border_style="cyan",
        )
        table.add_column(t("headers.id"), width=4)
        table.add_column(t("headers.name"), style="bold", width=12)
        table.add_column(t("headers.species"), width=10)
        table.add_column(t("headers.stage"), width=8)
        table.add_column(t("headers.age"), width=8)
        table.add_column(t("headers.status"), width=8)

        for p in pets:
            active = f"[bold green]{t('headers.active')}[/bold green]" if p.is_active else f"[dim]{t('headers.dormant')}[/dim]"
            from termipet.display.status_panel import _get_species_name
            table.add_row(
                str(p.id), p.name,
                _get_species_name(p.species_key),
                p.stage,
                f"{p.age_days:.1f}{t('data.day_suffix')}",
                active,
            )

        console.print(table)
    finally:
        session.close()


@cli.command("switch")
@click.argument("pet_id", type=int)
def switch_cmd(pet_id: int):
    """Switch active pet by ID"""
    from termipet.database import get_session
    from termipet.models.pet import Pet

    session = get_session()
    try:
        current = session.query(Pet).filter_by(is_active=True).first()
        if current:
            current.is_active = False

        target = session.get(Pet, pet_id)
        if target is None:
            console.print(f"[red]{t('common.not_found', id=pet_id)}[/red]")
            return

        target.is_active = True
        session.commit()
        console.print(f"[green]{t('common.switch_success', name=target.name)}[/green]")
    finally:
        session.close()


if __name__ == "__main__":
    cli()
