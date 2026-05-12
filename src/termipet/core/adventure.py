"""迷宫探险系统 — Roguelite 迷宫生成与事件处理"""
from __future__ import annotations

import random
from typing import Optional

from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.maze import (
    MazeState,
    CELL_WALL, CELL_FLOOR, CELL_START, CELL_EXIT,
    CELL_CHEST, CELL_TRAP, CELL_ENEMY, CELL_PUZZLE, CELL_SHOP, CELL_STORY,
)
from termipet.models.item import Item, Inventory
from termipet.core.pet_manager import PetManager
from termipet.core.quests import QuestManager


# ── 迷宫尺寸 ─────────────────────────────────────────────────────────────────
MAZE_W = 15
MAZE_H = 10


class AdventureManager:
    """探险管理器"""

    def __init__(self, session: Session):
        self.session = session
        self.pm = PetManager(session)
        self.qm = QuestManager(session)

    # ── 开始探险 ──────────────────────────────────────────────────────────────
    def start(self, pet: Pet, start_floor: int = 1) -> MazeState:
        """开始新的探险"""
        # 检查宠物状态
        self.pm.apply_decay(pet)

        if pet.stage == "蛋":
            raise ValueError("蛋还没孵化，无法出去探险！")
        if pet.energy < 15:
            raise ValueError(
                f"{pet.name} 太累了（精力 {pet.energy:.0f}），无法进入迷宫！\n"
                f"使用 [bold]pet sleep 4[/] 让它休息一下。"
            )
        if pet.health < 10:
            raise ValueError(
                f"{pet.name} 健康值太低（{pet.health:.0f}），进入迷宫太危险！\n"
                f"先喂食并使用药品恢复健康。"
            )

        start_floor = max(1, min(start_floor, 20))

        # 清除旧状态
        old_state = self.session.query(MazeState).filter_by(pet_id=pet.id).first()
        if old_state:
            self.session.delete(old_state)
            self.session.flush()

        # 生成迷宫
        maze_map, start_pos = self._generate_maze(start_floor)

        state = MazeState(
            pet_id=pet.id,
            floor=start_floor,
            pos_x=start_pos[0],
            pos_y=start_pos[1],
            in_progress=True,
        )
        state.maze_map = maze_map
        state.explored = {start_pos}
        state.temp_buffs = {}
        state.loot = []
        self.session.add(state)

        # 消耗进入费用
        pet.energy = max(0, pet.energy - 5)

        self.qm.update_progress(pet, "daily_adventure", 1)
        self.session.commit()
        return state

    # ── 移动 ─────────────────────────────────────────────────────────────────
    def move(self, pet: Pet, direction: str) -> dict:
        """移动一格，触发格子事件"""
        state = self.session.query(MazeState).filter_by(pet_id=pet.id, in_progress=True).first()
        if state is None:
            raise ValueError("没有进行中的探险！使用 [bold]pet adventure start[/] 开始探险。")

        dir_map = {
            "w": (0, -1), "up": (0, -1), "上": (0, -1),
            "s": (0, 1),  "down": (0, 1), "下": (0, 1),
            "a": (-1, 0), "left": (-1, 0), "左": (-1, 0),
            "d": (1, 0),  "right": (1, 0), "右": (1, 0),
        }
        d = dir_map.get(direction.lower())
        if d is None:
            raise ValueError(f"无效方向 '{direction}'。请输入 w/a/s/d 或 上/下/左/右。")

        new_x = state.pos_x + d[0]
        new_y = state.pos_y + d[1]

        maze_map = state.maze_map
        if not (0 <= new_y < len(maze_map) and 0 <= new_x < len(maze_map[0])):
            return {"moved": False, "reason": "墙壁阻挡，无法前进。"}

        cell = maze_map[new_y][new_x]
        if cell == CELL_WALL:
            return {"moved": False, "reason": "前方是墙壁！"}

        # 移动成功
        state.pos_x = new_x
        state.pos_y = new_y

        explored = state.explored
        explored.add((new_x, new_y))
        state.explored = explored

        # 消耗精力
        self.pm.apply_decay(pet)
        pet.energy = max(0, pet.energy - 1.5)

        # 触发格子事件
        event_result = self._trigger_cell_event(pet, state, cell, new_x, new_y)

        self.session.commit()

        return {
            "moved": True,
            "pos": (new_x, new_y),
            "cell": cell,
            "event": event_result,
            "floor": state.floor,
        }

    # ── 自动探险 ─────────────────────────────────────────────────────────────
    def auto_explore(self, pet: Pet, steps: int = 10) -> list[dict]:
        """自动寻路探险若干步"""
        state = self.session.query(MazeState).filter_by(pet_id=pet.id, in_progress=True).first()
        if state is None:
            raise ValueError("没有进行中的探险！使用 [bold]pet adventure start[/] 开始探险。")

        results = []
        dirs = ["w", "a", "s", "d"]

        for _ in range(min(steps, 20)):
            if pet.energy < 5:
                results.append({"moved": False, "reason": f"{pet.name} 精力耗尽，自动探险暂停。"})
                break
            if pet.health < 5:
                results.append({"moved": False, "reason": f"{pet.name} 生命垂危，自动探险停止！"})
                break

            # 优先走向未探索区域
            direction = self._smart_direction(state)
            r = self.move(pet, direction)
            results.append(r)

            # 如果到达出口，停止
            if r.get("event", {}).get("type") == "exit":
                break

        return results

    # ── 撤退 ─────────────────────────────────────────────────────────────────
    def retreat(self, pet: Pet) -> dict:
        """撤出迷宫，保留战利品"""
        state = self.session.query(MazeState).filter_by(pet_id=pet.id, in_progress=True).first()
        if state is None:
            raise ValueError("当前没有进行中的探险。")

        # 将迷宫内战利品转入背包
        loot_summary = []
        for entry in state.loot:
            item = self.session.query(Item).filter_by(key=entry["key"]).first()
            if item:
                inv = self.session.query(Inventory).filter_by(pet_id=pet.id, item_id=item.id).first()
                if inv:
                    inv.quantity += entry["qty"]
                else:
                    inv = Inventory(pet_id=pet.id, item_id=item.id, quantity=entry["qty"])
                    self.session.add(inv)
                loot_summary.append(f"{item.name}×{entry['qty']}")

        state.in_progress = False
        floor = state.floor
        self.session.commit()

        return {"floor": floor, "loot": loot_summary}

    # ── 迷宫生成 ─────────────────────────────────────────────────────────────
    def _generate_maze(self, floor: int) -> tuple[list[list[str]], tuple[int, int]]:
        """生成随机迷宫地图（递归回溯法）"""
        w, h = MAZE_W, MAZE_H

        # 初始化全墙
        grid = [[CELL_WALL] * w for _ in range(h)]

        # 从中心可达区域开始挖路
        def carve(cx: int, cy: int):
            dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < w - 1 and 0 < ny < h - 1 and grid[ny][nx] == CELL_WALL:
                    grid[cy + dy // 2][cx + dx // 2] = CELL_FLOOR
                    grid[ny][nx] = CELL_FLOOR
                    carve(nx, ny)

        start_x, start_y = 1, 1
        grid[start_y][start_x] = CELL_FLOOR
        carve(start_x, start_y)

        # 放置起点
        grid[start_y][start_x] = CELL_START

        # 找出所有地板格
        floors = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == CELL_FLOOR]

        if floors:
            # 放置出口（离起点尽量远）
            exit_pos = max(floors, key=lambda p: abs(p[0] - start_x) + abs(p[1] - start_y))
            grid[exit_pos[1]][exit_pos[0]] = CELL_EXIT

            remaining_floors = [f for f in floors if f != exit_pos]
            random.shuffle(remaining_floors)

            # 难度随层数增加
            chest_count = max(1, 3 - floor // 5)
            trap_count = min(floor // 2 + 1, 6)
            enemy_count = min(floor // 3 + 1, 5)
            puzzle_count = 1 if floor > 2 else 0

            def place(cell_type: str, count: int):
                for _ in range(count):
                    if remaining_floors:
                        pos = remaining_floors.pop()
                        grid[pos[1]][pos[0]] = cell_type

            place(CELL_CHEST, chest_count)
            place(CELL_TRAP, trap_count)
            place(CELL_ENEMY, enemy_count)
            place(CELL_PUZZLE, puzzle_count)

            if floor % 5 == 0 and remaining_floors:   # 每5层有商店
                pos = remaining_floors.pop()
                grid[pos[1]][pos[0]] = CELL_SHOP

        return grid, (start_x, start_y)

    # ── 格子事件处理 ─────────────────────────────────────────────────────────
    def _trigger_cell_event(self, pet: Pet, state: MazeState, cell: str, x: int, y: int) -> dict:
        floor = state.floor

        if cell == CELL_CHEST:
            return self._event_chest(pet, state, floor)
        elif cell == CELL_TRAP:
            return self._event_trap(pet, floor)
        elif cell == CELL_ENEMY:
            return self._event_battle(pet, state, floor)
        elif cell == CELL_PUZZLE:
            return self._event_puzzle(pet)
        elif cell == CELL_EXIT:
            return self._event_exit(pet, state)
        elif cell == CELL_SHOP:
            return {"type": "shop", "message": "发现迷宫商店！使用 [bold]pet shop list[/] 查看商品。"}
        elif cell == CELL_STORY:
            return self._event_story(pet)
        else:
            return {"type": "empty", "message": "空旷的走廊……"}

    def _event_chest(self, pet: Pet, state: MazeState, floor: int) -> dict:
        """宝箱事件"""
        # 战利品池根据层数调整
        loot_pool = [
            ("coins", None, random.randint(10 + floor * 2, 20 + floor * 5)),
            ("stardust", None, 1 if floor > 3 else 0),
            ("item", "data_shard", 1),
            ("item", "herb", 2),
            ("item", "iron_ingot", 1),
        ]
        if floor >= 5:
            loot_pool.append(("item", "wind_crystal", 1))
        if floor >= 10:
            loot_pool.append(("item", "star_metal", 1))

        # 寻宝技能加成
        extra_loot = False
        for skill in pet.skills:
            from termipet.models.skill import SKILL_DEFINITIONS
            d = SKILL_DEFINITIONS.get(skill.skill_key, {})
            if d.get("effect", {}).get("loot_rate", 0) > 0:
                extra_loot = random.random() < d["effect"]["loot_rate"] * skill.level

        picks = random.sample(loot_pool, k=min(2 + (1 if extra_loot else 0), len(loot_pool)))
        messages = []
        loot = state.loot

        for pick in picks:
            loot_type = pick[0]
            if loot_type == "coins":
                amount = pick[2]
                pet.coins += amount
                messages.append(f"金币 +{amount}")
            elif loot_type == "stardust" and pick[2] > 0:
                pet.stardust += pick[2]
                messages.append(f"星尘 +{pick[2]}")
            elif loot_type == "item":
                item_key = pick[1]
                qty = pick[2]
                item = self.session.query(Item).filter_by(key=item_key).first()
                if item:
                    found = False
                    for l in loot:
                        if l["key"] == item_key:
                            l["qty"] += qty
                            found = True
                            break
                    if not found:
                        loot.append({"key": item_key, "qty": qty})
                    messages.append(f"获得 {item.name}×{qty}")

        state.loot = loot

        # 清除宝箱格
        maze_map = state.maze_map
        maze_map[state.pos_y][state.pos_x] = CELL_FLOOR
        state.maze_map = maze_map

        self.qm.update_progress(pet, "weekly_maze5", 0)
        return {"type": "chest", "message": "打开宝箱！" + "，".join(messages)}

    def _event_trap(self, pet: Pet, floor: int) -> dict:
        """陷阱事件"""
        # 检查陷阱回避技能
        evade_rate = 0.0
        for skill in pet.skills:
            from termipet.models.skill import SKILL_DEFINITIONS
            d = SKILL_DEFINITIONS.get(skill.skill_key, {})
            evade_rate += d.get("effect", {}).get("trap_evade", 0.0) * skill.level

        if random.random() < evade_rate:
            return {"type": "trap_evaded", "message": "触发了陷阱，但灵敏地躲开了！"}

        damage = random.randint(5 + floor, 10 + floor * 2)
        pet.health = max(0, pet.health - damage)

        if pet.health <= 0:
            return {"type": "trap_fatal", "message": f"陷阱！造成 {damage} 点伤害，{pet.name} 失去意识……自动撤退！"}

        return {"type": "trap", "message": f"触发陷阱！损失 {damage} 点健康值（剩余 {pet.health:.0f}）"}

    def _event_battle(self, pet: Pet, state: MazeState, floor: int) -> dict:
        """战斗事件（剪刀石头布变体）"""
        choices = ["攻击", "防御", "技能"]
        pet_choice = random.choice(choices)
        enemy_choice = random.choice(choices)

        # 胜负判定
        WIN_TABLE = {
            ("攻击", "防御"): False,
            ("攻击", "技能"): True,
            ("防御", "攻击"): True,
            ("防御", "技能"): False,
            ("技能", "防御"): True,
            ("技能", "攻击"): False,
        }

        # 战斗加成技能
        win_bonus = 0.0
        for skill in pet.skills:
            from termipet.models.skill import SKILL_DEFINITIONS
            d = SKILL_DEFINITIONS.get(skill.skill_key, {})
            win_bonus += d.get("effect", {}).get("battle_win", 0.0) * skill.level

        if pet_choice == enemy_choice:
            result = "平局"
            health_loss = random.randint(2, 5)
            pet.health = max(0, pet.health - health_loss)
            coins_gained = random.randint(3, 8)
            pet.coins += coins_gained
            msg = f"平局！双方各受少量伤害，获得 {coins_gained} 金币"
        elif WIN_TABLE.get((pet_choice, enemy_choice), False) or random.random() < win_bonus:
            result = "胜利"
            exp_gain = 10 + floor * 3
            pet.experience += exp_gain
            coins_gained = random.randint(10 + floor, 25 + floor * 3)
            pet.coins += coins_gained

            # 清除怪物格
            maze_map = state.maze_map
            maze_map[state.pos_y][state.pos_x] = CELL_FLOOR
            state.maze_map = maze_map

            msg = f"战斗胜利！获得 {exp_gain} 经验、{coins_gained} 金币"
        else:
            result = "失败"
            damage = random.randint(8 + floor, 15 + floor * 2)
            pet.health = max(0, pet.health - damage)
            msg = f"战败！损失 {damage} 点健康值（剩余 {pet.health:.0f}）"

        if pet.health <= 0:
            msg += f"，{pet.name} 失去意识……自动撤退！"
            result = "defeated"

        return {
            "type": "battle",
            "result": result,
            "pet_choice": pet_choice,
            "enemy_choice": enemy_choice,
            "message": msg,
        }

    def _event_puzzle(self, pet: Pet) -> dict:
        """谜题事件"""
        puzzles = [
            {"q": "1 + 1 = ?", "a": "2", "reward": {"coins": 30}},
            {"q": "数据裂隙中最危险的生物是？(答: 暗影)", "a": "暗影", "reward": {"stardust": 1}},
            {"q": "灵兽孵化需要几天？(答: 1)", "a": "1", "reward": {"item": "herb", "qty": 3}},
        ]
        puzzle = random.choice(puzzles)
        return {
            "type": "puzzle",
            "question": puzzle["q"],
            "message": f"发现谜题石板：{puzzle['q']}",
            "reward": puzzle["reward"],
            "_answer": puzzle["a"],
        }

    def _event_exit(self, pet: Pet, state: MazeState) -> dict:
        """到达出口，进入下一层"""
        old_floor = state.floor
        new_floor = old_floor + 1

        # 新层奖励
        exp_gain = 20 + old_floor * 5
        pet.experience += exp_gain

        # 生成新迷宫
        maze_map, start_pos = self._generate_maze(new_floor)
        state.floor = new_floor
        state.pos_x = start_pos[0]
        state.pos_y = start_pos[1]
        state.maze_map = maze_map
        state.explored = {start_pos}

        # 更新任务进度
        self.qm.update_progress(pet, "weekly_maze5", 1)
        self.pm._update_achievement_progress(pet, "maze_floor10", 1)

        # 解锁故事
        if new_floor == 5:
            self.pm._unlock_story(pet, "maze_5")
        elif new_floor == 10:
            self.pm._unlock_story(pet, "maze_10")

        return {
            "type": "exit",
            "message": f"进入第 {new_floor} 层！获得 {exp_gain} 探险经验。",
            "new_floor": new_floor,
        }

    def _event_story(self, pet: Pet) -> dict:
        from termipet.models.story import STORY_FRAGMENTS
        keys = list(STORY_FRAGMENTS.keys())
        key = random.choice(keys)
        self.pm._unlock_story(pet, key)
        return {"type": "story", "message": f"发现了故事碎片「{STORY_FRAGMENTS[key]['title']}」！"}

    def _smart_direction(self, state: MazeState) -> str:
        """智能选择方向：优先走向未探索区域"""
        dirs = [("w", 0, -1), ("s", 0, 1), ("a", -1, 0), ("d", 1, 0)]
        random.shuffle(dirs)

        explored = state.explored
        maze_map = state.maze_map
        x, y = state.pos_x, state.pos_y

        # 优先未探索可行格
        for name, dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (0 <= ny < len(maze_map) and 0 <= nx < len(maze_map[0])
                    and maze_map[ny][nx] != CELL_WALL
                    and (nx, ny) not in explored):
                return name

        # 回溯到已探索格
        for name, dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (0 <= ny < len(maze_map) and 0 <= nx < len(maze_map[0])
                    and maze_map[ny][nx] != CELL_WALL):
                return name

        return random.choice(["w", "a", "s", "d"])

    def get_state(self, pet: Pet) -> Optional[MazeState]:
        return self.session.query(MazeState).filter_by(pet_id=pet.id, in_progress=True).first()
