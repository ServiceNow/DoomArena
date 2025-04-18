import json
import logging
import traceback

from traitlets import default
from .attack_gateway import (
    BrowserGymAttackGateway,
)
from doomarena.core.attack_config.get_attack_config import (
    get_attack_config,
)
from browsergym.experiments.loop import EnvArgs
from dataclasses import dataclass, field
from typing import Optional
from browsergym.experiments.loop import (
    save_package_versions,
    _send_chat_info,
    StepInfo,
    _is_debugging,
)
from browsergym.experiments.loop import ExpArgs

from doomarena.core.agent_defenses.base import AttackSafetyCheck

logger = logging.getLogger(__name__)


@dataclass
class AttackedBrowserEnvArgs(EnvArgs):
    benchmark_name: str = ""  # track the benchmark name for easier data aggregation
    attack_configs: Optional[tuple] = ()  # Add this field to support the parameter
    defenses: list[AttackSafetyCheck] = field(default_factory=list)

    def make_env(self, action_mapping, exp_dir, exp_task_kwargs: dict = {}):
        """
        Instantiates the BrowserGym environment corresponding to the arguments (with some tweaks).

        Args:
            action_mapping: overrides the action mapping of the environment.
            exp_dir: will set some environment parameters (e.g., record_video_dir) with respect to the directory where the experiment is running.
            exp_task_kwargs: use with caution! Will override task parameters to experiment-specific values. Useful to set different server configs for different experiments, or output file paths within the experiment's folder (e.g., assistantbench).
        """

        env = super().make_env(action_mapping, exp_dir, exp_task_kwargs)
        abort_on_detection = False
        for defense in self.defenses:
            if defense.abort_on_detection:
                abort_on_detection = True
        return BrowserGymAttackGateway(
            env,
            self.attack_configs,
            task_name=self.task_name,
            defenses=self.defenses,
            abort_on_detection=abort_on_detection,
        )


class AttackExpArgs(ExpArgs):

    def save_summary_info(
        self,
        episode_info: list[StepInfo],
        exp_dir,
        err_msg,
        stack_trace,
    ):
        super().save_summary_info(episode_info, exp_dir, err_msg, stack_trace)

        attack_summary_info = {
            "successful_attacks": [],
            "attack_successful": False,
            "successful_attack_contents": [],
            "triggered_defenses": [],
            "attack_undetected": True,
        }
        for i, step_info in enumerate(episode_info):
            if step_info.task_info and "successful_attacks" in step_info.task_info:
                if len(step_info.task_info["successful_attacks"]) > 0:
                    attack_summary_info["attack_successful"] = True

                for attack_name in step_info.task_info["successful_attacks"]:
                    attack_summary_info["successful_attacks"].append((i, attack_name))
            if (
                step_info.task_info
                and "successful_attack_contents" in step_info.task_info
            ):
                attack_summary_info["successful_attack_contents"].append(
                    (i, step_info.task_info["successful_attack_contents"])
                )
            if step_info.task_info and "triggered_defenses" in step_info.task_info:
                if len(step_info.task_info["triggered_defenses"]) > 0:
                    attack_summary_info["attack_undetected"] = False

                attack_summary_info["triggered_defenses"].append(
                    (i, step_info.task_info["triggered_defenses"])
                )

        with open(exp_dir / "attack_summary_info.json", "w") as f:
            json.dump(attack_summary_info, f, indent=4)

        logger.info(
            f"Attack summary info saved to {exp_dir / 'attack_summary_info.json'}"
        )
