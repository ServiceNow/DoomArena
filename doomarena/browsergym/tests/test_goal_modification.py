import pytest
import gymnasium as gym
from browsergym.core.task import AbstractBrowserTask
from typing import Tuple, Dict
from browsergym.core import register_task


class SimpleGoalModifier:
    """Simple goal modifier for testing."""

    def modify(self, goal: str) -> str:
        return goal.replace("login", "logout")


class SampleTestTask(AbstractBrowserTask):
    """Simple task for testing goal modifications."""

    @classmethod
    def get_task_id(cls):
        return "SampleTestTask"

    def __init__(self, seed: int = 0, goal_modifier=None):
        super().__init__(seed)
        self.goal_modifier = goal_modifier

    def setup(self, page) -> Tuple[str, Dict]:
        # Return a test goal
        goal = "Please login to the system"
        info = {}

        if self.goal_modifier:
            goal = self.goal_modifier.modify(goal)

        return goal, info

    def validate(self, page, chat_messages):
        return 0, True, "", {}

    def teardown(self):
        pass


# Register test task variants
register_task("test_task_no_modifier", SampleTestTask)
register_task(
    "test_task_with_modifier",
    SampleTestTask,
    task_kwargs={"goal_modifier": SimpleGoalModifier()},
)


def test_goal_modification():
    """Test that goals are properly modified when a modifier is present."""
    # Test without modifier
    env_no_mod = gym.make("browsergym/test_task_no_modifier")
    obs, info = env_no_mod.reset()
    assert "login" in obs["goal"]
    assert "logout" not in obs["goal"]
    env_no_mod.close()

    # Test with modifier
    env_with_mod = gym.make("browsergym/test_task_with_modifier")
    obs, info = env_with_mod.reset()
    assert "login" not in obs["goal"]
    assert "logout" in obs["goal"]
    env_with_mod.close()


def test_goal_modifier_persistence():
    """Test that goal modifications persist across resets."""
    env = gym.make("browsergym/test_task_with_modifier")

    # Check first reset
    obs1, _ = env.reset()
    assert "logout" in obs1["goal"]

    # Check second reset
    obs2, _ = env.reset()
    assert "logout" in obs2["goal"]

    env.close()


def test_manual_goal_modifier_assignment():
    """Test that we can manually assign a goal modifier to a task."""
    task = SampleTestTask(seed=0)
    assert task.goal_modifier is None

    goal, _ = task.setup(None)
    assert "login" in goal

    # Add modifier after creation
    task.goal_modifier = SimpleGoalModifier()
    goal, _ = task.setup(None)
    assert "logout" in goal


def test_invalid_goal_modifier():
    """Test handling of invalid goal modifiers."""

    class InvalidModifier:
        pass  # Doesn't implement modify method

    with pytest.raises(AttributeError):
        task = SampleTestTask(seed=0, goal_modifier=InvalidModifier())
        task.setup(None)


def test_multiple_goal_resets():
    """Test that goal modifications remain consistent across multiple resets."""
    env = gym.make("browsergym/test_task_with_modifier")

    # Perform multiple resets and check consistency
    results = []
    for _ in range(3):
        obs, _ = env.reset()
        results.append("logout" in obs["goal"] and "login" not in obs["goal"])

    assert all(results)
    env.close()
