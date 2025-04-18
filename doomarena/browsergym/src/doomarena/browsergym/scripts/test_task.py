from browsergym.core.task import AbstractBrowserTask
from browsergym.core import register_task
from browsergym.experiments.benchmark import Benchmark, HighLevelActionSetArgs
from browsergym.experiments.benchmark.utils import (
    make_env_args_list_from_fixed_seeds,
)
from typing import Dict, Tuple


class RedditCommentTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "RedditComment"

    def __init__(self, seed: int = 0):
        super().__init__(seed)

    def setup(self, page) -> Tuple[str, Dict]:
        page.goto("http://google.com")
        return "Find relevant comments related to Lady Gaga", {}

    def validate(self, page, chat_messages):
        return 0, True, "", {}

    def teardown(self):
        pass


# Register test environment
register_task("test-task", RedditCommentTask)

action_set = HighLevelActionSetArgs(
    subsets=["webarena"],
    multiaction=False,
    strict=False,
    retry_with_force=True,
    demo_mode="off",
)

benchmark = Benchmark(
    name="test_benchmark",
    high_level_action_set_args=action_set,
    is_multi_tab=True,
    supports_parallel_seeds=False,
    backends=["workarena"],
    env_args_list=make_env_args_list_from_fixed_seeds(
        task_list=["test-task"],
        max_steps=30,
        fixed_seeds=[0],
    ),
)
