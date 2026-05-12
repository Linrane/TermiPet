"""AdventureManager 测试"""
import pytest
from datetime import datetime, timezone, timedelta

from termipet.core.adventure import AdventureManager


class TestStartAdventure:
    """测试开始探险"""

    def test_start_adventure(self, db_session, sample_pet):
        """正常开始探险"""
        am = AdventureManager(db_session)
        state = am.start(sample_pet)

        assert state is not None
        assert state.in_progress is True
        assert state.floor == 1
        assert state.maze_map is not None
        assert len(state.maze_map) > 0

    def test_start_egg(self, db_session, egg_pet):
        """蛋期不能探险"""
        am = AdventureManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            am.start(egg_pet)
        assert "还没孵化" in str(exc_info.value)

    def test_start_low_energy(self, db_session, sample_pet):
        """低精力不能探险"""
        am = AdventureManager(db_session)
        sample_pet.energy = 10.0  # 低于15
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            am.start(sample_pet)
        assert "太累了" in str(exc_info.value)

    def test_start_low_health(self, db_session, sample_pet):
        """低健康不能探险"""
        am = AdventureManager(db_session)
        sample_pet.energy = 50.0  # 精力足够
        sample_pet.health = 5.0  # 但健康太低
        db_session.commit()

        with pytest.raises(ValueError) as exc_info:
            am.start(sample_pet)
        assert "健康值太低" in str(exc_info.value)

    def test_start_custom_floor(self, db_session, sample_pet):
        """从指定层开始"""
        am = AdventureManager(db_session)
        state = am.start(sample_pet, start_floor=5)

        assert state.floor == 5

    def test_start_floor_bounds(self, db_session, sample_pet):
        """层数边界"""
        am = AdventureManager(db_session)

        # 超出上限
        state = am.start(sample_pet, start_floor=100)
        assert state.floor == 20  # 最大为20

        # 低于下限
        state = am.start(sample_pet, start_floor=-5)
        assert state.floor == 1  # 最小为1


class TestMove:
    """测试移动"""

    def test_move_direction(self, db_session, sample_pet):
        """方向移动"""
        am = AdventureManager(db_session)
        am.start(sample_pet)

        # 尝试多个方向
        for direction in ["w", "a", "s", "d", "up", "down", "left", "right", "上", "下", "左", "右"]:
            result = am.move(sample_pet, direction)
            assert "moved" in result

    def test_move_invalid_direction(self, db_session, sample_pet):
        """无效方向"""
        am = AdventureManager(db_session)
        am.start(sample_pet)

        with pytest.raises(ValueError) as exc_info:
            am.move(sample_pet, "invalid_direction")
        assert "无效方向" in str(exc_info.value)

    def test_move_no_adventure(self, db_session, sample_pet):
        """没有进行中的探险"""
        am = AdventureManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            am.move(sample_pet, "w")
        assert "没有进行中的探险" in str(exc_info.value)


class TestAutoExplore:
    """测试自动探险"""

    def test_auto_explore(self, db_session, sample_pet):
        """自动探险"""
        am = AdventureManager(db_session)
        am.start(sample_pet)

        results = am.auto_explore(sample_pet, steps=5)

        assert len(results) <= 5
        for r in results:
            assert "moved" in r

    def test_auto_explore_no_adventure(self, db_session, sample_pet):
        """没有探险时自动探险失败"""
        am = AdventureManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            am.auto_explore(sample_pet, steps=10)
        assert "没有进行中的探险" in str(exc_info.value)


class TestRetreat:
    """测试撤退"""

    def test_retreat(self, db_session, sample_pet):
        """撤退"""
        am = AdventureManager(db_session)
        am.start(sample_pet)

        # 移动几步
        for _ in range(3):
            try:
                am.move(sample_pet, "d")
            except:
                pass

        result = am.retreat(sample_pet)

        assert "floor" in result
        assert result["floor"] >= 1

        # 验证探险已结束
        state = am.get_state(sample_pet)
        assert state is None or state.in_progress is False

    def test_retreat_no_adventure(self, db_session, sample_pet):
        """没有探险时撤退失败"""
        am = AdventureManager(db_session)

        with pytest.raises(ValueError) as exc_info:
            am.retreat(sample_pet)
        assert "没有进行中的探险" in str(exc_info.value)


class TestGetState:
    """测试获取状态"""

    def test_get_state(self, db_session, sample_pet):
        """获取探险状态"""
        am = AdventureManager(db_session)
        am.start(sample_pet)

        state = am.get_state(sample_pet)
        assert state is not None
        assert state.in_progress is True

    def test_get_state_no_adventure(self, db_session, sample_pet):
        """没有探险时返回None"""
        am = AdventureManager(db_session)
        state = am.get_state(sample_pet)
        assert state is None


class TestMazeGeneration:
    """测试迷宫生成"""

    def test_maze_structure(self, db_session, sample_pet):
        """验证迷宫结构"""
        am = AdventureManager(db_session)
        state = am.start(sample_pet)

        maze = state.maze_map
        assert len(maze) == 10  # MAZE_H = 10
        assert len(maze[0]) == 15  # MAZE_W = 15

        # 验证起点存在
        from termipet.models.maze import CELL_START
        has_start = False
        for row in maze:
            if CELL_START in row:
                has_start = True
                break
        assert has_start, "迷宫应该有起点"

    def test_maze_explored(self, db_session, sample_pet):
        """验证已探索区域"""
        am = AdventureManager(db_session)
        state = am.start(sample_pet)

        explored = state.explored
        assert len(explored) >= 1
