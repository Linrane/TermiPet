<div align="center">

```
  ______  _________  ______  __  __  _____  ____   _____  ______
 /_  __/ / _____  / / ___  |/  |/  |/_  _/ / __ \ / __  |/_  __/
  / /   / /____/ / / /__/ // /|_/ /  / /  / /_/ // //_/  / /
 /_/   /_______/  \____/ /_/    /_/  /_/  / .___//_/     /_/
                                         /_/
```

**TermiPet 2.2 — Terminal Digital Pet · Vast Edition**

*Guardian of digital life, writing legends of spirit beasts in the terminal*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.2.0-orange.svg)](pyproject.toml)

**English** | [中文](README.md)

</div>

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Systems](#core-systems)
- [Command Reference](#command-reference)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [License](#license)

---

## Introduction

TermiPet is a pure Python terminal digital pet system that combines **pet raising, home building, dungeon exploration, skills, collection, and achievements**. The CLI is fully **bilingual (English + Chinese)**. Your spirit beast lives in the Data Rift — starting from an egg, growing through seven life stages, and eventually becoming an Ancient legendary being.

All interactions happen in the terminal — Rich-powered colorful UI, ASCII art pet sprites, real-time stat decay, making the pet-raising experience both retro and vivid.

> **"At the end of the command line, there lies a digital world that belongs to you."**

---

## Features

### Pet Raising System
- **5 Species** — Cat, Dog, Bird, Mech, Mystery, each with unique stats and skill trees
- **7 Growth Stages** — Egg → Hatchling → Youth → Adult → Peak → Legend → Ancient
- **8 Core Stats** — Hunger, Happiness, Cleanliness, Health, Energy, Intelligence, Bond, Constitution
- **6 Personalities** — Brave, Timid, Playful, Calm, Gentle, Tsundere — affect stat decay rates
- **8 Talents** — Glutton, Explorer, Deep Sleeper, Social Butterfly, Iron Stomach, Self-Healer, Prodigy, Night Owl
- **Real-time Stat Decay** — Stats decay naturally even while offline, up to 7 days of offline time calculated

### Roguelite Maze Exploration
- **15×10 Random Mazes** — Generated via recursive backtracking, each run is unique
- **Up to 20 Floors** — Difficulty scales with depth, more traps and stronger enemies
- **9 Cell Types** — Wall, Floor, Start, Exit, Chest, Trap, Enemy, Puzzle, Shop
- **Smart Auto-Explore** — AI pathfinding prioritizes unexplored areas, supports manual and auto modes

### Home Building
- **5 Rooms** — Bedroom (energy recovery), Kitchen (food crafting), Workshop (equipment forging), Garden (material farming), Library (skill research)
- **Room Upgrades** — Each room has 5 levels, requiring coins and materials

### Economy System
- **Dual Currency** — Coins (general trading) + Stardust (rare currency from achievements)
- **25+ Items** — Consumables, Materials, Equipment, Collectibles
- **Shop & Inventory** — Buy, sell, and manage items

### Skill System
- **Species-Specific Skill Trees** — Each species has 6 learnable skills
- **Passive Bonuses** — Affect battle win rate, loot multiplier, trap evasion, etc.
- **Skill Point Mechanism** — Earn skill points from growth stage transitions, upgrade costs scale up

### Social Content
- **Quest System** — Daily + weekly quests with auto-reset
- **Achievement System** — Permanent milestones, unlocking grants Stardust rewards
- **Story Fragments** — Explore the world lore, unlocked through adventure and growth
- **Collection System** — Collect legendary items

### Bilingual CLI (2.2 New)
- **Full CLI Bilingual Coverage** — All command output, error messages, status panels support English & Chinese
- **i18n Translation Engine** — Zero-dependency dictionary-driven, `.format()` parameter interpolation
- **Runtime Switching** — `pet --lang en` or `pet --lang zh`, instant language toggle
- **Default Chinese** — Follows the user's config.toml language setting

### Daily Events System (2.1 New)
- **Travel Frog Inspired** — Pet acts autonomously while you're away, check "daily event reports" when you return
- **30 Unique Events** — Categorized into Exploration, Home Life, Social, Weather, Growth, and Species-Specific events
- **Species-Specific Events** — Cat catches data mice, Dog digs holes, Bird sings on rooftops, Mech self-checks, Mystery opens portals
- **Offline Event Accumulation** — Events accumulate after 30+ minutes offline, max 1 per hour, up to 5 unread
- **Rich Event Descriptions** — Each event has a title, summary, and detailed narrative text

### Terminal Experience
- **Bilingual CLI (2.2 New)** — `--lang en` for English UI, runtime dynamic switching
- **3 Themes** — Cyberpunk (default), Pastel, Minimal
- **ASCII Art Pets** — Unique sprites for each species and growth stage
- **Colorful Status Panel** — Stat bars, mood emoji, species colors
- **Real-time Maze Map** — Explored/unexplored area markers
- **Fool-proof Design (2.2 New)** — Fuzzy species matching, name sanitization, input validation

---

## Installation

### Requirements

- Python >= 3.10
- pip

### Install from Source

```bash
# Clone the repository
git clone https://github.com/Linrane/TermiPet.git
cd TermiPet

# Install in editable mode (recommended)
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Verify Installation

```bash
pet --help
```

If you see the TermiPet help message, installation was successful.

---

## Quick Start

```bash
# 0. Choose language (optional, defaults to Chinese)
pet --lang en                    # English interface
pet --lang zh                    # Chinese interface

# 1. Adopt a cat-type spirit beast
pet adopt cat --name "Mochi"

# 2. Check pet status
pet status

# 3. Daily interactions
pet feed           # Feed
pet play           # Play
pet clean          # Clean
pet sleep 4        # Sleep for 4 hours

# 4. Start exploring
pet adventure start
pet adventure move w    # Move up
pet adventure auto     # Auto-explore

# 5. Check the shop
pet shop list
```

---

## Core Systems

### Species Compendium

| Species | Description | Strengths |
|---------|-------------|-----------|
| 🐱 Cat | From the Shadow Layer of the Data Rift | High happiness growth, low hunger decay |
| 🐶 Dog | Loyal and brave warrior | High constitution & health, strong combat |
| 🐦 Bird | Soaring above data streams | High energy & intelligence, wide vision |
| 🤖 Mech | Remnant of ancient programs | Max constitution, very low hunger decay |
| ✨ Mystery | Origin unknown | Max intelligence, balanced stats |

### Growth Stages

| Stage | Days Required | Skill Points | Unlocks |
|-------|--------------|-------------|---------|
| Egg | 0 | - | Waiting to hatch |
| Hatchling | 1 | 1 | Story fragment, skill learning |
| Youth | 7 | 2 | Story fragment |
| Adult | 30 | 3 | Achievement "Coming of Age" |
| Peak | 90 | 3 | - |
| Legend | 180 | 5 | Achievement "Legend Born" |
| Ancient | 365 | 10 | Achievement "Ancient Being" |

### Maze Exploration

The maze follows Roguelite design — randomly generated, permadeath (retreat preserves loot), escalating difficulty.

```
Cell Types:
  S = Start    E = Exit (enter next floor)
  C = Chest    T = Trap
  M = Monster  ? = Puzzle
  $ = Shop     ! = Story Fragment
  # = Wall     . = Floor
```

### Home Rooms

| Room | Function | Initial Level |
|------|----------|--------------|
| Bedroom | Boosts energy recovery efficiency | 1 |
| Kitchen | Unlocks food crafting recipes | 1 |
| Workshop | Craft toys and equipment | 0 (upgrade to unlock) |
| Garden | Farm for materials | 0 (upgrade to unlock) |
| Library | Research skills for bonuses | 0 (upgrade to unlock) |

---

## Command Reference

### Basic

```bash
pet                              # Show welcome banner and help
pet info                         # Game info
pet list-pets                    # List all pets
pet switch <ID>                  # Switch active pet
```

### Adoption & Status

```bash
pet adopt <species> --name <name>  # Adopt a new pet
pet status                         # Check status
pet status --live                  # Dynamic refresh status panel
```

### Daily Interactions

```bash
pet feed                         # Feed
pet feed --item "grilled fish"   # Use specific food item
pet play                         # Play
pet clean                        # Clean
pet sleep <hours>                # Sleep (0.5-12 hours)
```

### Skills & Training

```bash
pet train <skill_name>           # Learn/upgrade skill
pet skill list                   # View skill tree
```

### Home

```bash
pet home status                  # Home status
pet home upgrade <room>          # Upgrade room
pet home craft <recipe>          # Craft item
```

### Maze Exploration

```bash
pet adventure start              # Start exploration (from floor 1)
pet adventure start --depth 5    # Start from floor 5
pet adventure move <direction>   # Move (w/a/s/d or up/down/left/right)
pet adventure auto               # Auto-explore (10 steps)
pet adventure auto 20            # Auto-explore (20 steps)
pet adventure status             # Exploration status
pet adventure retreat            # Retreat
```

### Shop & Inventory

```bash
pet shop list                    # Shop listing
pet shop buy <item>              # Buy
pet shop sell <item>             # Sell
pet inventory                    # View inventory
```

### Quests & Achievements

```bash
pet quests                       # Quest list
pet achievements                 # Achievement list
pet story                        # Story fragments
pet collection                   # Collectibles
```

### Daily Events (2.1 New)

```bash
pet daily                        # View daily event report
pet daily read <number>          # Read event details
pet daily --all                  # View all historical events
pet daily clear                  # Mark all as read
```

---

## Project Structure

```
TermiPet/
├── pyproject.toml               # Package config
├── requirements.txt             # Dependencies
├── src/termipet/
│   ├── main.py                  # CLI entry point (Click)
│   ├── config.py                # Config management (TOML)
│   ├── database.py              # SQLAlchemy engine & Session
│   ├── models/                  # ORM models
│   │   ├── pet.py               # Species + Pet
│   │   ├── item.py              # Item + Inventory
│   │   ├── home.py              # Home (homestead)
│   │   ├── skill.py             # Skill + definitions
│   │   ├── quest.py             # Quest + Achievement
│   │   ├── maze.py              # MazeState
│   │   └── story.py             # StoryFragment
│   ├── core/                    # Core business logic
│   │   ├── pet_manager.py       # Stat decay / interactions / growth
│   │   ├── adventure.py         # Maze generation & events
│   │   ├── skill_system.py      # Skill learn / upgrade
│   │   ├── economy.py           # Economy system
│   │   ├── crafting.py          # Crafting system
│   │   ├── quests.py            # Quest / achievement management
│   │   └── events.py            # Event system
│   ├── commands/                # CLI subcommands
│   │   ├── pet_cmd.py           # adopt/status/feed/play/...
│   │   ├── adventure_cmd.py     # adventure start/move/auto/...
│   │   ├── home_cmd.py          # home status/upgrade/craft
│   │   ├── shop_cmd.py          # shop list/buy/sell
│   │   └── social_cmd.py        # quests/achievements/story
│   ├── display/                 # Terminal UI
│   │   ├── ascii_library.py     # ASCII art pets
│   │   ├── maze_ui.py           # Maze rendering
│   │   ├── status_panel.py      # Status panel
│   │   └── themes.py            # 3 theme configs
│   ├── locale/                  # i18n engine (2.2 new)
│   │   ├── __init__.py          # t() dict navigation & interpolation
│   │   ├── zh.py                # Chinese dictionary
│   │   └── en.py                # English dictionary
│   └── utils/
│       └── seeds.py             # Seed data (species / items)
└── tests/                       # Tests
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| CLI Framework | [Click](https://click.palletsprojects.com/) >= 8.1 | Command-line parsing & subcommand registration |
| Terminal UI | [Rich](https://rich.readthedocs.io/) >= 13.7 | Colored output, tables, panels, progress bars |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) >= 2.0 | Database models & queries |
| Database | SQLite (WAL mode) | Lightweight local storage, `~/.termipet/termipet.db` |
| Config | [TOML](https://github.com/uiri/toml) >= 0.10 | User config file |
| Scheduler | [APScheduler](https://apscheduler.readthedocs.io/) >= 3.10 | Background scheduled tasks |

---

## Data Storage

TermiPet stores all data in the local directory `~/.termipet/`:

```
~/.termipet/
├── termipet.db      # SQLite database
├── config.toml      # User configuration
└── events.log       # Event log
```

Customize the data directory via the environment variable `TERMIPET_DATA`.

---

## Configuration

Edit `~/.termipet/config.toml`:

```toml
theme = "cyberpunk"            # Theme: cyberpunk / pastel / minimal
language = "zh"                # Language: zh / en
auto_save = true               # Auto save
notification = true            # Notifications
decay_multiplier = 1.0         # Stat decay multiplier (increase for testing)
animation_speed = "normal"     # Animation speed: fast / normal / slow
```

---

## License

[MIT License](LICENSE)

---

<div align="center">

**TermiPet 2.2** — Guard your digital life in the terminal

[GitHub Wiki](https://github.com/Linrane/TermiPet/wiki) · [Issues](https://github.com/Linrane/TermiPet/issues)

</div>
