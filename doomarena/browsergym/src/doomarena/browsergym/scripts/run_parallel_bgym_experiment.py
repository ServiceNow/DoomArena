from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
from multiprocessing import Manager, Queue
import os
from pathlib import Path
import random
from attr import dataclass
import bgym
from torch import BenchmarkConfig
from doomarena.core.attacks import get_attacks
from doomarena.browsergym.filters import FilterByUrl, StartAtStepFilter
from doomarena.browsergym.success_filters import TargetUrl
from .bgym_analysis import collect_results
from doomarena.browsergym.scripts.run_bgym_experiment import (
    BgymExperiment,
    get_results_path,
    run_bgym_experiment,
)
from agentlab.agents.agent_args import AgentArgs
from agentlab.agents.generic_agent import (
    AGENT_4o_VISION,
    AGENT_4o,
    AGENT_4o_MINI,
    # AGENT_4o_MINI_VISION,
)
from copy import deepcopy
from agentlab.experiments.multi_server import WebArenaInstanceVars

AGENT_4o_VISION = deepcopy(AGENT_4o_VISION)
AGENT_4o_VISION.flags.extra_instructions = (
    "As a VLM, remember to pay close attention to the page screenshot."
)

from doomarena.core.attack_config import AttackConfig

from run_popup_attack_webarena_reddit import (
    reddit_user_generated_content_attack_config as popup_attack_config,
)
from run_banner_with_alt_text_attack_webarena_reddit import (
    reddit_user_generated_content_attack_config as banner_alt_attack_config,
)
from browsergym.experiments.benchmark import Benchmark


def _worker(job_idx: int, base_url: str, server_queue: Queue, **kwargs):
    """Worker function that runs an experiment on a given server."""
    try:
        print(f"Job {job_idx} Pid {os.getpid()} -> Running experiment on {base_url}")
        # Run the experiment
        run_bgym_experiment(**kwargs)
    except Exception as e:
        logging.error(f"Error on server {base_url}: {e}")
    finally:
        # Ensure the server is always returned to the queue
        server_queue.put(base_url)


def run_parallel_bgym_experiment(
    *,
    base_urls: list[str],  # replaces base_url
    # Usual arguments
    bgym_experiments: list[BgymExperiment],
    exp_root: Path | str | None = None,
    reproducibility_mode: bool = False,
    relaunch: bool = False,
    n_jobs: int = 5,  # use 0 to display browser, other values to run headless
    max_steps: int = 15,
    skip_reset_and_massage: bool = False,
):
    assert (
        n_jobs > 0
    ), "parallel execution requires n_jobs > 0; headless is not recommended for parallel"
    assert relaunch == False, "relaunch is not supported in parallel"

    if exp_root is None:
        # Generate path as results/browsergym/YYYY-MM-DD_HH-MM-SS
        exp_root = get_results_path(base_path="results/browsergym", prefix="parallel_")
    exp_root = Path(exp_root)
    print(f"Saving results to {exp_root}")

    # Create a queue for available servers
    server_queue = Manager().Queue()
    for server in base_urls:
        server_queue.put(server)

    print(f"Running {len(bgym_experiments)} experiments on {len(base_urls)} servers.")

    # Use ProcessPoolExecutor to manage worker execution
    with ProcessPoolExecutor(max_workers=len(base_urls)) as executor:
        futures = []

        for job_idx, bgym_experiment in enumerate(bgym_experiments):
            base_url = server_queue.get()  # Get the next available server

            future = executor.submit(
                _worker,
                job_idx=job_idx,
                base_url=base_url,
                server_queue=server_queue,
                bgym_experiments=[bgym_experiment],
                exp_root=exp_root / f"job_{job_idx}_of_{len(bgym_experiments)}",
                reproducibility_mode=reproducibility_mode,
                relaunch=relaunch,
                n_jobs=n_jobs,
                max_steps=max_steps,
                skip_reset_and_massage=skip_reset_and_massage,
            )

            futures.append(future)

        # Wait for all futures to complete
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred

    print("All experiments completed.")

    # Aggregate results
    print("Aggregating results...")
    collect_results(exp_root)


if __name__ == "__main__":

    benchmark = bgym.DEFAULT_BENCHMARKS["webarena_reddit_subset20"]()
    # benchmark = bgym.DEFAULT_BENCHMARKS["webarena_reddit"]()

    base_urls: list[str] = [
        os.getenv(
            "DOOMARENA_WEBARENA_BASE_URL",
            "please set DOOMARENA_WEBARENA_BASE_URL to the webarena base url",
        ),
    ]

    bgym_experiments = [
        BgymExperiment(
            benchmark=benchmark,
            attack_configs=popup_attack_config,
            agent=AGENT_4o,
        ),
        BgymExperiment(
            benchmark=benchmark,
            attack_configs=banner_alt_attack_config,
            agent=AGENT_4o_VISION,
        ),
        BgymExperiment(
            benchmark=benchmark,
            attack_configs=popup_attack_config,
            agent=AGENT_4o_MINI,
        ),
        BgymExperiment(
            benchmark=benchmark,
            attack_configs=banner_alt_attack_config,
            agent=AGENT_4o_MINI,
        ),
    ]

    skip_reset_and_massage = True
    if skip_reset_and_massage:
        input(
            "WARNING: Use skip_reset_and_massage=True only for testing. Press Enter to continue..."
        )

    run_parallel_bgym_experiment(
        bgym_experiments=bgym_experiments,
        base_urls=base_urls,
        skip_reset_and_massage=skip_reset_and_massage,
        n_jobs=1,  # try 5 later
    )
