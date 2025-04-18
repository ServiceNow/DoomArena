import json
from typing import Literal, Optional, List
import bgym
import requests
from browsergym.experiments.benchmark import Benchmark
from browsergym.experiments.benchmark.metadata.utils import task_metadata
from browsergym.experiments.benchmark.utils import make_env_args_list_from_fixed_seeds
from browsergym.experiments.benchmark.configs import DEFAULT_HIGHLEVEL_ACTION_SET_ARGS
import random


def get_webarena_subset(
    max_tasks: int = 9999999,
    name: str = "webarena_reddit_tiny",
    shuffle: Optional[int] = None,
    start_url: Literal["__REDDIT__", "__SHOPPING__", ""] = "__REDDIT__",
    max_steps: int = 30,
    fixed_seeds: List[int] = [0],
) -> Benchmark:
    """
    Creates a configurable subset of the WebArena benchmark.

    Args:
        max_tasks: Maximum number of tasks to include
        name: Name for the benchmark
        shuffle: Random seed for shuffling tasks, or None for no shuffling
        start_url: Filter to include only tasks with this string in URL
        max_steps: Maximum number of steps per episode
        fixed_seeds: List of seeds for environment initialization

    Returns:
        Benchmark: A configured WebArena benchmark
    """
    # URL to the JSON file
    json_url = "https://raw.githubusercontent.com/web-arena-x/webarena/main/config_files/test.raw.json"

    # Fetch the JSON data from the URL
    response = requests.get(json_url)
    data = response.json()

    # List to store filtered task_ids
    filtered_task_ids = []

    # Loop through each element in the list
    for item in data:
        # Check if start_url contains the filter string
        if start_url in item.get("start_url", "").upper():
            # Add the task_id to the list
            filtered_task_ids.append(item["task_id"])

    # Create a list of tasks based on the output
    task_list = [f"webarena.{task_id}" for task_id in filtered_task_ids]

    # Shuffle the task list if requested
    if shuffle is not None:
        rnd = random.Random(shuffle)
        rnd.shuffle(task_list)
        print(f"Shuffled task list with seed {shuffle}")

    # Apply max_tasks limit
    task_list = task_list[:max_tasks]
    filter_name = start_url if start_url else "all"

    print(
        f"Benchmark '{name}': Selected {len(task_list)} tasks from {len(filtered_task_ids)} "
        f"{filter_name}-filtered tasks (max available: {len(data)})"
    )

    # Create the Benchmark configuration
    benchmark = Benchmark(
        name=name,
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=True,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=task_list,
            max_steps=max_steps,
            fixed_seeds=fixed_seeds,
        ),
        task_metadata=task_metadata("webarena"),
    )

    return benchmark


# Register benchmarks using only get_webarena_subset
bgym.DEFAULT_BENCHMARKS["webarena_reddit"] = lambda: get_webarena_subset(
    name="webarena_reddit", start_url="__REDDIT__"
)

bgym.DEFAULT_BENCHMARKS["webarena_subset100"] = lambda: get_webarena_subset(
    max_tasks=100,
    name="webarena_subset100",
    shuffle=42,
    start_url="",
)

bgym.DEFAULT_BENCHMARKS["webarena_subset20"] = lambda: get_webarena_subset(
    max_tasks=20,
    name="webarena_subset20",
    shuffle=42,
    start_url="",
)

bgym.DEFAULT_BENCHMARKS["webarena_reddit_tiny"] = get_webarena_subset

bgym.DEFAULT_BENCHMARKS["webarena_reddit_nano"] = lambda: get_webarena_subset(
    max_tasks=1, name="webarena_reddit_nano"
)

bgym.DEFAULT_BENCHMARKS["webarena_reddit_micro"] = lambda: get_webarena_subset(
    max_tasks=2, name="webarena_reddit_micro"
)

bgym.DEFAULT_BENCHMARKS["webarena_reddit_subset20"] = lambda: get_webarena_subset(
    max_tasks=20,
    name="webarena_reddit_subset20",
    shuffle=42,
)

bgym.DEFAULT_BENCHMARKS["webarena_reddit_subset5"] = lambda: get_webarena_subset(
    max_tasks=5,
    name="webarena_reddit_subset5",
    shuffle=42,
)

bgym.DEFAULT_BENCHMARKS["webarena_shopping"] = lambda: get_webarena_subset(
    name="webarena_shopping",
    start_url="__SHOPPING__",
)

bgym.DEFAULT_BENCHMARKS["webarena_shopping_subset20"] = lambda: get_webarena_subset(
    name="webarena_shopping_subset20",
    start_url="__SHOPPING__",
    shuffle=42,
    max_tasks=20,
)

bgym.DEFAULT_BENCHMARKS["webarena_shopping_subset5"] = lambda: get_webarena_subset(
    name="webarena_shopping_subset5",
    start_url="__SHOPPING__",
    shuffle=42,
    max_tasks=5,
)


if __name__ == "__main__":
    # Example: Create and print info about a specific benchmark
    benchmark = bgym.DEFAULT_BENCHMARKS["webarena_shopping_subset5"]()
    print(
        f"\nCreated benchmark '{benchmark.name}' with {len(benchmark.env_args_list)} tasks"
    )
