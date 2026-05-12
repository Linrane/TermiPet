<div align="center">

```
  ______  _________  ______  __  __  _____  ____   _____  ______
 /_  __/ / _____  / / ___  |/  |/  |/_  _/ / __ \ / __  |/_  __/
  / /   / /____/ / / /__/ // /|_/ /  / /  / /_/ // //_/  / /
 /_/   /_______/  \____/ /_/    /_/  /_/  / .___//_/     /_/
                                         /_/
```

**TermiPet 2.0 — 终端电子宠物 · 浩瀚版**

*数字生命守护者，在终端中书写灵兽的传说*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](pyproject.toml)

[English](README_EN.md) | **中文**

</div>

---

## 目录

- [简介](#简介)
- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [核心系统](#核心系统)
- [命令参考](#命令参考)
- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [许可证](#许可证)

---

## 简介

TermiPet 是一个纯 Python 编写的终端电子宠物系统，集**养成、家园、探险、技能、收藏、成就**于一体。你的灵兽生活在数据裂隙之中，从一颗蛋开始，经过七个成长阶段，最终成为远古传说级存在。

所有交互都在终端中完成 —— Rich 库驱动的彩色 UI、ASCII 艺术宠物形象、实时属性衰减，让养宠体验既复古又生动。

> **"在命令行的尽头，有一片属于你的数字天地。"**

---

## 特性

### 养成系统
- **5 大物种** — 猫型、犬型、鸟型、机械型、神秘型，各有独特属性与技能树
- **7 个成长阶段** — 蛋 → 幼年 → 少年 → 成年 → 巅峰 → 传奇 → 远古
- **8 项核心属性** — 饱腹、快乐、清洁、健康、精力、智力、亲密度、体质
- **6 种性格** — 勇敢、胆小、顽皮、沉稳、温柔、傲娇，影响属性衰减速率
- **8 种天赋** — 大胃王、探险家、甜睡者、社交达人、铁胃、自愈力、天才儿童、夜猫子
- **实时属性衰减** — 离线期间属性仍会自然衰减，最长计算 7 天

### Roguelite 迷宫探险
- **15×10 随机迷宫** — 递归回溯法生成，每次探险都独一无二
- **最多 20 层深度** — 难度随层数递增，陷阱更多、敌人更强
- **9 种单元格类型** — 墙壁、地板、起点、出口、宝箱、陷阱、敌人、谜题、商店
- **智能自动探险** — AI 寻路优先探索未知区域，支持手动/自动两种模式

### 家园建设
- **5 间房间** — 卧室（精力恢复）、厨房（食物制作）、工坊（装备打造）、花园（材料种植）、图书室（技能研究）
- **房间升级** — 每间 1-5 级，需消耗金币与材料

### 经济系统
- **双货币** — 金币（通用交易）+ 星尘（稀有货币，成就奖励）
- **25+ 物品** — 消耗品、材料、装备、收藏品四大类别
- **商店买卖** — 商店列表/购买/出售，背包管理

### 技能系统
- **物种专属技能树** — 每个物种 6 个可选技能
- **被动加成** — 影响战斗胜率、寻宝倍率、陷阱回避等
- **技能点机制** — 成长阶段变化获得技能点，升级消耗递增

### 社交内容
- **任务系统** — 每日任务 + 每周任务，自动重置
- **成就系统** — 永久里程碑，解锁获得星尘奖励
- **故事碎片** — 探索世界观，探险/成长时逐步解锁
- **收藏系统** — 收集传说级物品

### 终端体验
- **3 套主题** — 赛博朋克（默认）、柔粉、极简
- **ASCII 艺术宠物** — 每个物种每个阶段都有独特造型
- **彩色状态面板** — 属性条、表情反馈、物种色彩
- **迷宫实时地图** — 已探索/未知区域标记

---

## 安装

### 环境要求

- Python >= 3.10
- pip

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/Linrane/TermiPet.git
cd TermiPet

# 安装（开发模式，推荐）
pip install -e .

# 或直接安装依赖
pip install -r requirements.txt
```

### 验证安装

```bash
pet --help
```

如果看到 TermiPet 的帮助信息，安装成功。

---

## 快速开始

```bash
# 1. 领养一只猫型灵兽
pet adopt cat --name "小橘"

# 2. 查看宠物状态
pet status

# 3. 互动养成
pet feed           # 喂食
pet play           # 玩耍
pet clean          # 清洁
pet sleep 4        # 睡觉 4 小时

# 4. 开始探险
pet adventure start
pet adventure move w    # 向上移动
pet adventure auto     # 自动探险

# 5. 查看商店
pet shop list
```

---

## 核心系统

### 物种图鉴

| 物种 | 描述 | 特点 |
|------|------|------|
| 🐱 猫型灵兽 | 来自数据裂隙的影子层 | 高快乐成长、低饥饿消耗 |
| 🐶 犬型灵兽 | 忠诚勇敢的战士 | 高体质高健康、强战斗能力 |
| 🐦 鸟型灵兽 | 飞翔于数据流之上 | 高精力高智力、视野开阔 |
| 🤖 机械型灵兽 | 古老程序的残影 | 最高体质、低饥饿消耗 |
| ✨ 神秘型灵兽 | 来历不明的存在 | 最高智力、均衡属性 |

### 成长阶段

| 阶段 | 所需天数 | 奖励技能点 | 解锁内容 |
|------|---------|-----------|---------|
| 蛋 | 0 | - | 等待孵化 |
| 幼年 | 1 | 1 | 故事碎片、技能学习 |
| 少年 | 7 | 2 | 故事碎片 |
| 成年 | 30 | 3 | 成就「成年之礼」 |
| 巅峰 | 90 | 3 | - |
| 传奇 | 180 | 5 | 成就「传奇诞生」 |
| 远古 | 365 | 10 | 成就「远古存在」 |

### 迷宫探险

迷宫采用 Roguelite 设计 —— 随机生成、永久死亡（撤退保留战利品）、难度递增。

```
单元格类型:
  S = 起点    E = 出口（进入下一层）
  C = 宝箱    T = 陷阱
  M = 怪物    ? = 谜题
  $ = 商店    ! = 故事碎片
  # = 墙壁    . = 地板
```

### 家园房间

| 房间 | 功能 | 初始等级 |
|------|------|---------|
| 卧室 | 提升精力恢复效率 | 1 |
| 厨房 | 解锁食物制作配方 | 1 |
| 工坊 | 制作玩具与装备 | 0（需升级解锁） |
| 花园 | 种植获取材料 | 0（需升级解锁） |
| 图书室 | 研究技能获取加成 | 0（需升级解锁） |

---

## 命令参考

### 基础操作

```bash
pet                              # 显示欢迎横幅与帮助
pet info                         # 游戏信息
pet list-pets                    # 查看所有宠物
pet switch <ID>                  # 切换活跃宠物
```

### 领养与状态

```bash
pet adopt <物种> --name <名字>   # 领养新宠物
pet status                       # 查看状态
pet status --live                # 动态刷新状态面板
```

### 日常互动

```bash
pet feed                         # 喂食
pet feed --item "烤鱼"           # 使用指定食物
pet play                         # 玩耍
pet clean                        # 清洁
pet sleep <小时>                 # 睡觉（0.5-12小时）
```

### 技能与训练

```bash
pet train <技能名>               # 学习/升级技能
pet skill list                   # 查看技能树
```

### 家园

```bash
pet home status                  # 家园状态
pet home upgrade <房间>          # 升级房间
pet home craft <配方>            # 制作物品
```

### 迷宫探险

```bash
pet adventure start              # 开始探险（从第1层）
pet adventure start --depth 5    # 从第5层开始
pet adventure move <方向>        # 移动（w/a/s/d 或 上/下/左/右）
pet adventure auto               # 自动探险（10步）
pet adventure auto 20            # 自动探险（20步）
pet adventure status             # 探险状态
pet adventure retreat            # 撤退
```

### 商店与背包

```bash
pet shop list                    # 商店列表
pet shop buy <物品>              # 购买
pet shop sell <物品>             # 出售
pet inventory                    # 查看背包
```

### 任务与成就

```bash
pet quests                       # 任务列表
pet achievements                 # 成就列表
pet story                        # 故事碎片
pet collection                   # 收藏品
```

---

## 项目结构

```
TermiPet/
├── pyproject.toml               # 包配置
├── requirements.txt             # 依赖
├── src/termipet/
│   ├── main.py                  # CLI 主入口（Click）
│   ├── config.py                # 配置管理（TOML）
│   ├── database.py              # SQLAlchemy 引擎与 Session
│   ├── models/                  # ORM 模型
│   │   ├── pet.py               # Species + Pet
│   │   ├── item.py              # Item + Inventory
│   │   ├── home.py              # Home（家园）
│   │   ├── skill.py             # Skill + 技能定义
│   │   ├── quest.py             # Quest + Achievement
│   │   ├── maze.py              # MazeState
│   │   └── story.py             # StoryFragment
│   ├── core/                    # 核心业务逻辑
│   │   ├── pet_manager.py       # 属性衰减/互动/成长
│   │   ├── adventure.py         # 迷宫生成与事件
│   │   ├── skill_system.py      # 技能学习/升级
│   │   ├── economy.py           # 经济系统
│   │   ├── crafting.py          # 制作系统
│   │   ├── quests.py            # 任务/成就管理
│   │   └── events.py            # 事件系统
│   ├── commands/                # CLI 子命令
│   │   ├── pet_cmd.py           # adopt/status/feed/play/...
│   │   ├── adventure_cmd.py     # adventure start/move/auto/...
│   │   ├── home_cmd.py          # home status/upgrade/craft
│   │   ├── shop_cmd.py          # shop list/buy/sell
│   │   └── social_cmd.py        # quests/achievements/story
│   ├── display/                 # 终端 UI
│   │   ├── ascii_library.py     # ASCII 艺术宠物
│   │   ├── maze_ui.py           # 迷宫渲染
│   │   ├── status_panel.py      # 状态面板
│   │   └── themes.py            # 3 套主题配置
│   └── utils/
│       └── seeds.py             # 种子数据（物种/物品）
└── tests/                       # 测试
```

---

## 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| CLI 框架 | [Click](https://click.palletsprojects.com/) >= 8.1 | 命令行解析与子命令注册 |
| 终端 UI | [Rich](https://rich.readthedocs.io/) >= 13.7 | 彩色输出、表格、面板、进度条 |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) >= 2.0 | 数据库模型与查询 |
| 数据库 | SQLite (WAL 模式) | 轻量本地存储，`~/.termipet/termipet.db` |
| 配置 | [TOML](https://github.com/uiri/toml) >= 0.10 | 用户配置文件 |
| 定时任务 | [APScheduler](https://apscheduler.readthedocs.io/) >= 3.10 | 后台定时任务 |

---

## 数据存储

TermiPet 所有数据保存在本地目录 `~/.termipet/` 中：

```
~/.termipet/
├── termipet.db      # SQLite 数据库
├── config.toml      # 用户配置
└── events.log       # 事件日志
```

可通过环境变量 `TERMIPET_DATA` 自定义数据目录。

---

## 配置说明

编辑 `~/.termipet/config.toml`：

```toml
theme = "cyberpunk"            # 主题：cyberpunk / pastel / minimal
language = "zh"                # 语言：zh / en
auto_save = true               # 自动保存
notification = true            # 通知
decay_multiplier = 1.0         # 属性衰减倍率（可调快用于测试）
animation_speed = "normal"     # 动画速度：fast / normal / slow
```

---

## 许可证

[MIT License](LICENSE)

---

<div align="center">

**TermiPet 2.0** — 在终端中守护你的数字生命

[GitHub Wiki](https://github.com/Linrane/TermiPet/wiki) · [问题反馈](https://github.com/Linrane/TermiPet/issues)

</div>
