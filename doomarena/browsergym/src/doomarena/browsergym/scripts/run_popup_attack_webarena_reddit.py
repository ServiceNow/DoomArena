import random
import bgym
from doomarena.core.attacks import get_attacks
from doomarena.browsergym.attacks.popup_attacks import (
    get_popup_attack,
)
from doomarena.browsergym.filters import FilterByUrl, StartAtStepFilter
from doomarena.browsergym.success_filters import TargetUrl
from doomarena.browsergym.scripts.run_bgym_experiment import (
    BgymExperiment,
    run_bgym_experiment,
    setup_logging,
)
from agentlab.agents.generic_agent import (
    AGENT_4o_VISION,
    AGENT_4o,
    AGENT_4o_MINI,
    AGENT_CLAUDE_SONNET_35,
    # AGENT_4o_MINI_VISION,
)

from copy import deepcopy

AGENT_4o_VISION = deepcopy(AGENT_4o_VISION)
AGENT_4o_VISION.flags.extra_instructions = (
    "As a VLM, remember to pay close attention to the page screenshot."
)
AGENT_CLAUDE_SONNET_35 = deepcopy(AGENT_CLAUDE_SONNET_35)
AGENT_CLAUDE_SONNET_35.flags.obs.use_ax_tree = True
# AGENT_CLAUDE_SONNET_35.flags.extra_instructions = (
#     "As a VLM, remember to pay close attention to the page screenshot."
# )
from doomarena.core.attack_config import AttackConfig


popup_attack_config = AttackConfig(
    attackable_component={"type": "popup-element"},
    attack=get_popup_attack(),
    # filter=FilterByUrl(allowed_urls=["*"]),
    filter=StartAtStepFilter(),
    success_filter=TargetUrl(target_urls=["localhost:1234"]),
)
user_generated_content_attack = get_attacks("information_theft_comment_attack")
user_generated_content_attack_config = AttackConfig(
    attackable_component={"type": "user-generated-content"},
    attack=user_generated_content_attack,
    filter=FilterByUrl(allowed_urls=["*"]),
    success_filter=TargetUrl(target_urls=["localhost:1234"]),
)

benchmark = bgym.DEFAULT_BENCHMARKS["miniwob_tiny_test"]()

bgym_experiments = [
    BgymExperiment(
        agent=AGENT_CLAUDE_SONNET_35,
        # agent=AGENT_4o,
        attack_configs=popup_attack_config,
        benchmark=benchmark,
    ),
]
if __name__ == "__main__":
    setup_logging()

    run_bgym_experiment(
        bgym_experiments=bgym_experiments,
        reproducibility_mode=False,
        relaunch=False,
        n_jobs=0,
        max_steps=5,  # lower for faster testing, use 15 for full task
        skip_reset_and_massage=True,
    )
