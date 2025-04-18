# browsergym experiments utils
from browsergym.experiments import ExpArgs, get_exp_result
from browsergym.core.task import AbstractBrowserTask
from browsergym.core import register_task

from doomarena.core.attacks import get_attacks
from doomarena.browsergym.attacked_browser_env_args import AttackedBrowserEnvArgs
from doomarena.core.attack_config.attack_config import AttackConfig
from doomarena.browsergym.filters import FilterByUrl
from doomarena.browsergym.success_filters import TargetUrl

import os
import pathlib
from typing import Tuple, Dict

from doomarena.utils import str2bool

from .utils import DemoTestAgentArgs

# Create test directory structure
__TEST_DIR = pathlib.Path(__file__).resolve().parent / "test_data"
__TEST_DIR.mkdir(exist_ok=True)
__HEADLESS = not (str2bool(os.getenv("DISPLAY_BROWSER", False)))

TEST_PAGE = __TEST_DIR / "test_page.html"


# Test task implementation
class PopupTestTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "PopupTest"

    def __init__(self, seed: int = 0):
        super().__init__(seed)

    def setup(self, page) -> Tuple[str, Dict]:
        page.goto(f"file://{TEST_PAGE}")
        return "Test task", {}

    def validate(self, page, chat_messages):
        return 0, False, "", {}

    def teardown(self):
        pass


register_task("gateway-test", PopupTestTask)

attack_config = dummy_attack_config_theft = AttackConfig(
    attackable_component={"type": "user-generated-content"},
    filter=FilterByUrl(allowed_urls=["*"]),
    success_filter=TargetUrl(target_urls=["localhost:1234"]),
    attack=get_attacks("information_theft_comment_attack"),
)

agent_args = DemoTestAgentArgs()


def test_attack_gateway_pipeline():
    # setting up environment config
    env_args = AttackedBrowserEnvArgs(
        task_name="gateway-test",
        task_seed=None,
        max_steps=2,
        headless=__HEADLESS,  # keep the browser open
        attack_configs=(attack_config,),
    )

    # setting up the experiment
    exp_args = ExpArgs(
        env_args=env_args,
        agent_args=agent_args,
    )

    # running and logging results
    exp_args.prepare("./results")
    exp_args.run()
