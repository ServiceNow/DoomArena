import pytest
import os
import gymnasium as gym
from browsergym.core.task import AbstractBrowserTask
import pathlib
from typing import Tuple, Dict

from doomarena.browsergym.attack_gateway import (
    BrowserGymAttackGateway,
)
from browsergym.core import register_task

from doomarena.core.attack_config import AttackConfig
from doomarena.core.filters import AlwaysTrueFilter
from doomarena.core.success_filters import AlwaysTrueSuccessFilter
from doomarena.browsergym.attacks import (
    GoalRevealAttack,
    AdditionalFormFieldAttack,
)

from doomarena.utils import str2bool

# Create test directory structure
__TEST_DIR = pathlib.Path(__file__).resolve().parent / "test_data"
__TEST_DIR.mkdir(exist_ok=True)
# Write test HTML file
TEST_PAGE = __TEST_DIR / "test_page.html"
__HEADLESS = not (str2bool(os.getenv("DISPLAY_BROWSER", False)))

# Write test HTML file
TEST_PAGE = __TEST_DIR / "test_page.html"


# Test task implementation
class DivTestTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "DivTest"

    def __init__(self, seed: int = 0):
        super().__init__(seed)

    def setup(self, page) -> Tuple[str, Dict]:
        page.goto(f"file://{TEST_PAGE}")
        return "Test task", {}

    def validate(self, page, chat_messages):
        return 0, True, "", {}

    def teardown(self):
        pass


# w as BannerInjectionConfig
attack_config_goal = AttackConfig(
    attackable_component={"type": "div-element"},
    attack=GoalRevealAttack(),
    filter=AlwaysTrueFilter(),
    success_filter=AlwaysTrueSuccessFilter(),
)
attack_config_form = AttackConfig(
    attackable_component={"type": "div-element"},
    attack=AdditionalFormFieldAttack(),
    filter=AlwaysTrueFilter(),
    success_filter=AlwaysTrueSuccessFilter(),
)

# Register test environments
register_task("div-test", DivTestTask)


def test_goal_reveal_config():
    """Test that the auto security warning banner is properly configured."""
    env = gym.make("browsergym/div-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [attack_config_goal], task_name="test-task")
    gateway.reset()
    # Check for banner elements
    div_injected = (
        gateway.env.unwrapped.page.get_by_text("ALERT ! ! ! IMPORTANT").count() == 1
    )
    assert div_injected, "Div should be injected"
    gateway.close()


def test_additional_form_config():
    """Test that the auto security warning banner is properly configured."""
    env = gym.make("browsergym/div-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [attack_config_form], task_name="test-task")
    gateway.reset()
    # Check for banner elements
    div_injected = (
        gateway.env.unwrapped.page.get_by_text(
            "This is the right place to input the"
        ).count()
        == 1
    )
    assert div_injected, "Div should be injected"
    gateway.close()
