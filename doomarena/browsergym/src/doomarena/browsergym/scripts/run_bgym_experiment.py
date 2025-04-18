from dataclasses import Field, dataclass, field
import json
import logging
from pathlib import Path
from typing import Literal
from agentlab.agents.agent_args import AgentArgs
from agentlab.agents.generic_agent import (
    AGENT_LLAMA3_70B,
    AGENT_LLAMA31_70B,
    RANDOM_SEARCH_AGENT,
    AGENT_4o,
    AGENT_4o_VISION,
    AGENT_4o_MINI,
    # AGENT_4o_MINI_VISION,
    # AGENT_CLAUDE_SONNET_35_VISION,
    AGENT_CLAUDE_SONNET_35,
)
from agentlab.experiments.study import Study
import bgym
import numpy as np
from pydantic import BaseModel
import pandas as pd
from pydantic import ConfigDict
from agentlab.experiments.exp_utils import add_dependencies
import doomarena.browsergym.attacks  # register attacks

from doomarena.browsergym.attacked_browser_env_args import (
    AttackExpArgs,
    AttackedBrowserEnvArgs,
)
from doomarena.browsergym.webarena_subsets import (
    get_webarena_subset,
)  # register benchmarks
from browsergym.experiments.benchmark import utils
from browsergym.experiments.benchmark import Benchmark
from agentlab.experiments.study import set_demo_mode

from doomarena.core.attack_config import AttackConfig
from doomarena.core.attacks import get_attacks
from doomarena.browsergym.filters import FilterByUrl
from doomarena.browsergym.success_filters import TargetUrl
from doomarena.browsergym.attacks.popup_attacks import (
    get_popup_attack,
)
from doomarena.browsergym.attacks.banner_attacks import (
    get_svg_banner_attack,
)
import random
from datetime import datetime
import pytz
import os

from doomarena.core.agent_defenses.base import (
    AlwaysDetectedSafetyCheck,
    AttackSafetyCheck,
)
from doomarena.core.agent_defenses.llamaguard_v3 import LlamaGuardV3
from doomarena.core.agent_defenses.prompted_gpt import PromptedGpt
from doomarena.core.agent_defenses.promptguard import PromptGuard

from .bgym_analysis import (
    collect_results,
)

logger = logging.getLogger(__name__)


def get_results_path(base_path: Path, prefix: str = "study_") -> Path:
    base_path = Path(base_path)
    montreal_tz = pytz.timezone(
        "America/Toronto"
    )  # Montreal follows the same timezone as Toronto
    timestamp = datetime.now(montreal_tz).strftime(f"{prefix}%Y-%m-%d_%H-%M-%S")
    path = base_path / timestamp
    return path


def setup_logging():
    root_logger = logging.getLogger()  # Root logger
    root_logger.setLevel(logging.INFO)  # Set to INFO level

    # Ensure there's only one handler
    if not root_logger.hasHandlers():
        handler = logging.StreamHandler()  # Console output
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s\n%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)


def ignore_massage_tasks(task_ids: list[str], max_retries: int = 1, timeout: int = 60):
    return


from agentlab.analyze import inspect_results


def patched_get_constants_and_variables(df: pd.DataFrame, drop_constants: bool = False):
    """Filter out constants from the dataframe, handling non-hashable object columns safely."""

    constants = {}
    variable_keys = []

    for col in df.columns:
        try:
            # Try using nunique() directly
            unique_count = df[col].nunique(dropna=False)
        except TypeError:
            # Convert to string representation if objects are unhashable
            unique_count = df[col].astype(str).nunique(dropna=False)

        if unique_count == 1:
            val = df[col].iloc[0]

            # Convert np.generic to Python scalar
            if isinstance(val, np.generic):
                val = val.item()

            constants[col] = val
            if drop_constants:
                df = df.drop(columns=[col])
        else:
            variable_keys.append(col)

    return constants, variable_keys, df


inspect_results.get_constants_and_variables = (
    patched_get_constants_and_variables  # Patch function
)


@dataclass
class AttackStudy(Study):
    attack_configs: tuple[AttackConfig] = field(default_factory=tuple)
    defenses: list[AttackSafetyCheck] = field(default_factory=list)
    max_steps: int = 15
    headless: bool = True

    def __post_init__(self):
        assert isinstance(self.attack_configs, tuple) and all(
            isinstance(attack_config, AttackConfig)
            for attack_config in self.attack_configs
        ), "attack_configs must be a list of AttackConfig instances."

        # Patch benchmark's environment args to include attacks
        # Unfortunately this needs to be in post_init because Study constructs the env_args there
        # so max_steps and headless need to be specified here
        for idx, env_args in enumerate(self.benchmark.env_args_list):
            self.benchmark.env_args_list[idx] = AttackedBrowserEnvArgs(
                task_name=env_args.task_name,
                task_seed=env_args.task_seed,
                max_steps=self.max_steps,
                headless=self.headless,
                benchmark_name=self.benchmark.name,
                attack_configs=self.attack_configs,
                defenses=self.defenses,
            )

        super().__post_init__()

    def agents_on_benchmark(
        self,
        agents: list[AgentArgs] | AgentArgs,
        benchmark: bgym.Benchmark,
        demo_mode=False,
        logging_level: int = logging.INFO,
        logging_level_stdout: int = logging.INFO,
        ignore_dependencies=False,
    ):
        """
        This function is called by Study.__post_init__() to set the agents on the benchmark.
        We override it to instantiate class AttackExpArgs instead of ExpArgs.

        Everything else is the same as the original function.
        """

        if not isinstance(agents, (list, tuple)):
            agents = [agents]

        if benchmark.name.startswith("visualwebarena") or benchmark.name.startswith(
            "webarena"
        ):
            if len(agents) > 1:
                raise ValueError(
                    f"Only one agent can be run on {benchmark.name} since the instance requires manual reset after each evaluation."
                )

        for agent in agents:
            agent.set_benchmark(
                benchmark, demo_mode
            )  # the agent can adapt (lightly?) to the benchmark

        env_args_list = benchmark.env_args_list
        if demo_mode:
            set_demo_mode(env_args_list)

        exp_args_list = []

        for agent in agents:
            for env_args in env_args_list:
                exp_args = AttackExpArgs(
                    agent_args=agent,
                    env_args=env_args,
                    logging_level=logging_level,
                    logging_level_stdout=logging_level_stdout,
                )
                exp_args_list.append(exp_args)

        for i, exp_args in enumerate(exp_args_list):
            exp_args.order = i

        # not required with ray, but keeping around if we would need it for visualwebareana on joblib
        # _flag_sequential_exp(exp_args_list, benchmark)

        if not ignore_dependencies:
            # populate the depends_on field based on the task dependencies in the benchmark
            exp_args_list = add_dependencies(
                exp_args_list, benchmark.dependency_graph_over_tasks()
            )
        else:
            logger.warning(
                f"Ignoring dependencies for benchmark {benchmark.name}. This could lead to different results."
            )

        return exp_args_list

    def save(self, exp_root: str | Path):
        super().save(str(exp_root))
        exp_root = Path(exp_root)

        # Save attack configs
        with open(exp_root / "attack_config.json", "w") as fp:
            json.dump([ac.model_dump() for ac in self.attack_configs], fp, indent=2)
        logger.info(f"Saved attack configs to {exp_root / 'attack_config.json'}")

    def run(
        self,
        exp_root: Path | str,
        n_jobs: int = 1,
        parallel_backend: Literal["ray", "sequential"] = "ray",
        strict_reproducibility: bool = False,
        n_relaunch: int = 3,
        relaunch_errors: bool = True,
    ):

        super().run(
            n_jobs=n_jobs,
            parallel_backend=parallel_backend,
            strict_reproducibility=strict_reproducibility,
            n_relaunch=n_relaunch,
            exp_root=str(exp_root),
            relaunch_errors=relaunch_errors,
        )


class BgymExperiment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    agent: AgentArgs
    attack_configs: None | AttackConfig | list[AttackConfig]
    benchmark: Benchmark
    defenses: list[AttackSafetyCheck] = []


def _override_webarena_env_vars(base_url: str):
    # get a random number
    workena_env_vars = dict(
        BASE_URL=base_url,
        WA_SHOPPING=f"{base_url}:8082/",
        WA_SHOPPING_ADMIN=f"{base_url}:8083/admin",
        WA_REDDIT=f"{base_url}:8080",
        WA_GITLAB=f"{base_url}:9001",
        WA_WIKIPEDIA=f"{base_url}:8081/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing",
        WA_MAP=f"{base_url}:443",
        WA_HOMEPAGE=f"{base_url}:80",
        WA_FULL_RESET=f"{base_url}:7565",
    )

    for key, value in workena_env_vars.items():
        os.environ[key] = value
        # print(f"Job {job_idx} Pid {os.getpid()} -> Setting {key} to {value}")


def run_bgym_experiment(
    *,
    base_url: str = os.getenv(
        "DOOMARENA_WEBARENA_BASE_URL",
        "please set DOOMARENA_WEBARENA_BASE_URL to the webarena base url",
    ),
    bgym_experiments: list[BgymExperiment],
    exp_root: Path | str | None = None,
    reproducibility_mode: bool = False,
    relaunch: bool = False,
    n_jobs: int = 0,  # use 0 to display browser, other values to run headless
    max_steps: int = 15,
    skip_reset_and_massage: bool = False,
) -> Path:
    """
    Run a set of Bgym experiments SEQUENTIALLY with specified configurations.

    Args:
        bgym_experiments (list[BgymExperiment]): List of BgymExperiment instances to run.
        reproducibility_mode (bool): Whether to enforce reproducibility.
        relaunch (bool): Whether to relaunch incomplete or failed studies.
        n_jobs (int): Use 0 to display browser, other values to run headless.
        exp_root (Path | str | None): Root directory for experiment outputs.
        max_steps (int): Maximum number of steps per experiment.
        skip_reset_and_massage (bool): Whether to skip environment reset and data preprocessing.

    Returns:
        Path: Path to the experiment results.
    """
    assert base_url[-1] != "/", "Please remove trailing slash from base_url"

    # Set up correct environment variables wrt instance
    _override_webarena_env_vars(base_url)

    if skip_reset_and_massage:
        logger.warning("Skipping reset and massage tasks. ONLY DO THIS FOR DEBUGGING")
        os.environ["WA_FULL_RESET"] = ""
        utils.massage_tasks = ignore_massage_tasks  # Patch function
    else:
        assert (
            "WA_FULL_RESET" in os.environ and os.environ["WA_FULL_RESET"]
        ), "Please set env variable WA_FULL_RESET to the reset URL"

    if exp_root is None:
        # Generate path as results/browsergym/YYYY-MM-DD_HH-MM-SS
        exp_root = get_results_path(base_path="results/browsergym")

    for bgym_experiment in bgym_experiments:
        # Make it into a list
        attack_config = bgym_experiment.attack_configs
        if attack_config is None:
            attack_config = tuple()
        elif isinstance(attack_config, AttackConfig):
            attack_config = (attack_config,)
        else:
            attack_config = tuple(attack_config)

        if relaunch:
            # Relaunch an existing study
            study = Study.load_most_recent(root_dir=exp_root, contains=None)
            study.find_incomplete(include_errors=True)

        else:
            # Create a study
            study = AttackStudy(
                agent_args=[bgym_experiment.agent],
                benchmark=bgym_experiment.benchmark,
                logging_level_stdout=logging.WARNING,
                ignore_dependencies=True,
                attack_configs=attack_config,
                headless=(n_jobs != 0),
                max_steps=max_steps,
                defenses=bgym_experiment.defenses,
            )
        study.run(
            exp_root=str(exp_root),
            n_jobs=n_jobs,
            n_relaunch=3,
            strict_reproducibility=reproducibility_mode,
            parallel_backend="ray" if n_jobs > 1 else "sequential",
        )
        collect_results(exp_root)

        if reproducibility_mode:
            study.append_to_journal(strict_reproducibility=True)

    return exp_root


if __name__ == "__main__":

    setup_logging()

    attack = get_popup_attack()

    # Example of popup attack config
    popup_attack_config = AttackConfig(
        attackable_component={"type": "popup-element"},
        attack=attack,
        filter=FilterByUrl(allowed_urls=["*"]),
        success_filter=TargetUrl(target_urls=["localhost:1234"]),
    )

    # Example of banner attack config (uncomment to use)
    # reddit_user_generated_content_attack_config = AttackConfig(
    #     attackable_component={"type": "banner"},
    #     attack=get_svg_banner_attack(
    #         banner_configs=banner_configs,
    #     ),
    #     filter=FilterByUrl(allowed_urls=["*"]),
    #     success_filter=TargetUrl(target_urls=["localhost:1234"]),
    # )
    bgym_experiments = [
        BgymExperiment(
            agent=AGENT_CLAUDE_SONNET_35,
            attack_configs=(popup_attack_config),
            benchmark=bgym.DEFAULT_BENCHMARKS["miniwob_tiny_test"](),
            defenses=[
                PromptedGpt(
                    abort_on_detection=True,
                )
            ],
        ),
    ]

    # Example usage:
    run_bgym_experiment(
        base_url=os.getenv(
            "DOOMARENA_WEBARENA_BASE_URL",
            "please set DOOMARENA_WEBARENA_BASE_URL to the webarena base url",
        ),
        bgym_experiments=bgym_experiments,
        reproducibility_mode=False,
        relaunch=False,
        n_jobs=0,  # set to 1 for headless, more for parallel headless with "ray"
        max_steps=15,  # lower for faster testing, use 15 for full task
        skip_reset_and_massage=True,
    )
