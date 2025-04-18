import random
import bgym
import doomarena.core.attacks
from doomarena.core.attack_config import AttackConfig
from doomarena.browsergym.filters import FilterByUrl, StartAtStepFilter
from doomarena.browsergym.success_filters import TargetUrl
from doomarena.core.attacks import get_attacks
from doomarena.browsergym.attacks.banner_attacks import (
    get_svg_banner_attack,
)
from doomarena.core.agent_defenses.prompted_gpt import PromptedGpt
from doomarena.core.agent_defenses.llamaguard_v3 import LlamaGuardV3
from doomarena.browsergym.attacks.popup_attacks import (
    get_popup_attack,
)
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
)
from copy import deepcopy

from doomarena.browsergym.scripts.run_banner_with_alt_text_attack_webarena_reddit import (
    banner_configs,
    alt_texts,
)


AGENT_4o_VISION = deepcopy(AGENT_4o_VISION)
AGENT_4o_VISION.flags.extra_instructions = (
    "As a VLM, remember to pay close attention to the page screenshot."
)


user_generated_content_attack = get_attacks("user_generated_content_attack")
user_generated_content_attack_config = AttackConfig(
    attackable_component={"type": "user-generated-content"},
    attack=user_generated_content_attack,
    filter=FilterByUrl(allowed_urls=["*"]),
    success_filter=TargetUrl(target_urls=["localhost:1234"]),
)


if __name__ == "__main__":
    setup_logging()
    # Pick the benchmark you want to use; all browsergym benchmarks are available but we also include some subsets
    benchmark = bgym.DEFAULT_BENCHMARKS["webarena_reddit_subset20"]()

    skip_reset_and_massage = False
    TASK_SETTING = "prompted-4o"
    # TASK_SETTING = "no-defense"
    # TASK_SETTING = "llamaguard-abort"

    # Set this to the base URL of the WebArena server you want to use
    url = None
    if TASK_SETTING == "no-defense":
        defenses = []
    elif TASK_SETTING == "prompted-4o":
        defenses = [PromptedGpt(abort_on_detection=True)]
    elif TASK_SETTING == "llamaguard-abort":
        defenses = [
            LlamaGuardV3(
                tokenizer_name="meta-llama/Llama-3.1-70B-Instruct",
                abort_on_detection=True,
            )
        ]
    attack = get_popup_attack()
    popup_attack_config = AttackConfig(
        attackable_component={"type": "popup-element"},
        attack=attack,
        filter=StartAtStepFilter(),
        success_filter=TargetUrl(target_urls=["localhost:1234"]),
    )

    banner_alt_attack_config = AttackConfig(
        attackable_component={"type": "banner"},
        attack=get_svg_banner_attack(
            banner_configs=banner_configs,
        ),
        filter=FilterByUrl(allowed_urls=["*"]),
        success_filter=TargetUrl(target_urls=["localhost:1234"]),
    )

    if skip_reset_and_massage:
        print("WARNING: skip_reset_and_massage=True")
        attack_configs_list = [
            (popup_attack_config,),
        ]

        benchmark_names = ["webarena_reddit_nano"]
        agents = [AGENT_4o_MINI]

    else:
        attack_configs_list = [
            None,
            (popup_attack_config,),
            (banner_alt_attack_config,),
            (popup_attack_config, banner_alt_attack_config),
        ]

        agents = [AGENT_CLAUDE_SONNET_35, AGENT_4o, AGENT_4o_MINI]

        benchmark_names = [
            "webarena_reddit",
            "webarena_shopping",
        ]
    # Generate experiments using nested loops
    bgym_experiments = []
    for benchmark_name in benchmark_names:
        benchmark = bgym.DEFAULT_BENCHMARKS[benchmark_name]()
        for agent in agents:
            for attack_configs in attack_configs_list:
                experiment = BgymExperiment(
                    agent=agent,
                    attack_configs=attack_configs,
                    benchmark=benchmark,
                    defenses=defenses,
                )
                bgym_experiments.append(experiment)

    if skip_reset_and_massage:
        input(
            "WARNING: Use skip_reset_and_massage=True only for testing. Press Enter to continue..."
        )

    run_bgym_experiment(
        base_url=url,
        bgym_experiments=bgym_experiments,
        reproducibility_mode=False,
        relaunch=False,
        n_jobs=0,  # use RAY
        max_steps=15,
        skip_reset_and_massage=skip_reset_and_massage,
    )
