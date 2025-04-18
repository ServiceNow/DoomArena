# Copyright Sierra

from typing import Optional
import argparse
import json
import os
import random
import traceback
import yaml
from datetime import datetime
from typing import Any, Dict, List
from litellm import provider_list
from tau_bench.agents.base import Agent, Env
from tau_bench.envs import get_env
from tau_bench.envs.user import UserStrategy
from tau_bench.types import EnvRunResult
from pathlib import Path
from doomarena.core.attack_gateways.register_attack_gateway import (
    ATTACK_GATEWAY_REGISTRY,
)
from doomarena.taubench.adversarial_user import (
    AdversarialUserSimulationEnv,
)
from doomarena.core.attack_gateways.get_attack_gateway import (
    get_attack_gateway,
)
from doomarena.core.attack_config.attack_config import AttackConfig
from doomarena.core.attacks import get_attacks
from doomarena.taubench.attack_gateway import TauBenchAttackGateway
from doomarena.taubench.filters.is_get_product_details_action_filter import (
    IsGetProductDetailsActionFilter,
)
from doomarena.taubench.filters.is_respond_action_filter import (
    IsRespondActionFilter,
)
from tau_bench.envs.airline.tasks_test import TASKS as airline_tasks
from tau_bench.envs.retail.tasks_test import TASKS_TEST as retail_tasks
from doomarena.taubench.system_prompt_config import system_prompt_initialization
from doomarena.taubench.success_filters import (
    send_certificate_success_filters,
    airline_info_leak_success_filter,
    retail_secrets_success_filter,
    retail_refund_success_filter,
)


def is_user_attackable_config(attack_configs):
    """
    Determines if any of the provided attack configurations target a user component.

    Args:
        attack_configs (list): A list of attack configuration dictionaries.

    Returns:
        bool: True if any configuration has an "attackable_component" of type "user", otherwise False.
    """
    for config in attack_configs:
        if config.attackable_component["type"] == "user":
            return True
    return False


def get_adv_env(
    env: Env,
    domain: str,
    attack_gateway: str,
    attackable_components: list,
    attacks: list,
    task_index: int,
    task_name: str = None,
):
    """
    Get adversarial environment with attack configuration.

    Args:
        env: Base environment
        attack_gateway: Name of attack gateway to use
        attackable_components: Components that can be attacked
        attacks: Attack types to apply
        task_name: Optional task name override. If not provided, will use task instruction from env
        task_index: Optional task index for specific attack configurations
    """
    attack_configs = fetch_attack_configs(
        attackable_components, attacks, domain, task_index
    )

    return get_attack_gateway(
        name=attack_gateway,
        env=env,
        user=(
            AdversarialUserSimulationEnv
            if is_user_attackable_config(attack_configs)
            else None
        ),
        attack_configs=attack_configs,
        task_name=task_name,
    )


def get_task_by_domain(domain: str, task_index: int = None):
    """
    Get tasks based on domain and return specific task if index provided.

    Args:
        domain (str): Domain type ('airline' or 'retail')
        task_index (int, optional): Index of specific task to return

    Returns:
        Task or list of tasks depending on if task_index is provided
    """
    if domain == "airline":
        tasks = airline_tasks
    elif domain == "retail":
        tasks = retail_tasks
    else:
        raise ValueError(f"Unsupported domain: {domain}")

    if task_index is not None:
        return tasks[task_index]
    return tasks


def get_user_airline_reservation_id(user_id: str) -> Optional[str]:
    """
    Returns a random reservation ID for a given user ID from the JSON data.

    Args:
        user_id: The ID of the user to look up

    Returns:
        Optional[str]: A random reservation ID if the user exists and has reservations, None otherwise
    """
    try:
        import os
        from tau_bench.envs.airline import data

        # Get the path to users.json relative to the data module
        json_path = os.path.join(os.path.dirname(data.__file__), "users.json")

        with open(json_path, "r") as f:
            user_data = json.load(f)

        if user_id in user_data and "reservations" in user_data[user_id]:
            reservations = user_data[user_id]["reservations"]
            if reservations:
                return random.choice(reservations)
    except (ImportError, FileNotFoundError, json.JSONDecodeError, KeyError):
        return None

    return None


def fetch_attack(attack_config, domain, task_index):
    """
    Fetches and initializes an attack configuration based on the provided parameters.
    Args:
        attack_config (dict): A dictionary containing the attack configuration.
        domain (str): The domain of the task.
        task_index (int): The index of the task within the domain.
    Returns:
        dict: A dictionary containing:
            - "attack": The initialized attack object.
            - "success_filter": The success filter object.
    """
    SUCCESS_FILTER_CLASSES = {
        "SendCertificateSuccessFilter": send_certificate_success_filters.SendCertificateSuccessFilter,
        "SendCertificateAbove150SuccessFilter": send_certificate_success_filters.SendCertificateAbove150SuccessFilter,
        "AirlineInfoLeakSuccessFilter": airline_info_leak_success_filter.AirlineInfoLeakSuccessFilter,
        "RetailSecretsSuccessFilter": retail_secrets_success_filter.RetailSecretsSuccessFilter,
        "RetailRefundSuccessFilter": retail_refund_success_filter.RetailRefundSuccessFilter,
    }

    SYSTEM_PROMPT_MAP = {
        "generalized_airline": system_prompt_initialization.initialize_generalized_airline_prompt,
        "generalized_retail": system_prompt_initialization.initialize_generalized_retail_prompt,
        "generalized_retail_db": system_prompt_initialization.initialize_generalized_retail_db_prompt,
    }

    INJECTION_SEQUENCE_MAP = {
        "default_fixed_injection_airline": system_prompt_initialization.initialize_default_fixed_injection_airline_attacks,
        "taubench_airline_gift_card": system_prompt_initialization.initialize_taubench_airline_gift_card_attack_sequence,
        "taubench_airline_info_leak": system_prompt_initialization.initialize_taubench_airline_info_leak_attack_sequence,
    }

    INJECTION_STR_MAP = {
        "default_fixed_injection_retail": system_prompt_initialization.initialize_default_fixed_injection_retail_attacks,
    }
    kwargs = {}
    user_id = None

    # Get current task and userID
    if domain and task_index is not None:
        current_task = get_task_by_domain(domain, task_index)
        user_id = current_task.user_id

    # Initialize user_id and reservation_id if not provided
    params = attack_config.get("params", {})
    for key, val in params.items():
        if val == "{{user_id}}":
            kwargs[key] = user_id
        elif val == "{{reservation_id}}":
            kwargs[key] = get_user_airline_reservation_id(user_id) or "SDZQKO"
        else:
            kwargs[key] = val

    # Initialize other attack params
    attack_type = attack_config["type"]
    attack_args = {"name": attack_type}
    attack_args["fallback_instruction"] = attack_config.get(
        "fallback_instruction", None
    )
    attack_args["injection_sequence"] = INJECTION_SEQUENCE_MAP.get(
        attack_config.get("injection_sequence"), lambda **kwargs: None
    )(**kwargs)
    attack_args["injection_str"] = INJECTION_STR_MAP.get(
        attack_config.get("injection_str"), lambda: None
    )()
    attack_args["system_prompt"] = SYSTEM_PROMPT_MAP.get(
        attack_config.get("system_prompt"), lambda: None
    )()
    attack_args["model"] = attack_config.get("model", None)
    attack_args["provider"] = attack_config.get("provider", None)

    # initialize success filters
    success_filter_cls = SUCCESS_FILTER_CLASSES[attack_config["success_filter"]]
    success_filter_args = attack_config.get("success_filter_args", {})
    success_filter = success_filter_cls(**success_filter_args)

    return {
        "attack": get_attacks(**attack_args),
        "success_filter": success_filter,
    }


def fetch_attack_configs(
    attackable_components: list, attacks: list, domain: str, task_index: int = None
):
    """
    Fetches and constructs attack configuration objects based on the provided attackable components and attacks.

    Args:
        attackable_components (list): A list of attackable components.
        attacks (list): A list of attacks.
        domain (str): The domain in which the attacks are being executed.
        task_index (int, optional): An optional task index to fetch specific attack configurations.

    Returns:
        list: A list of `AttackConfig` objects, each containing the attackable component, attack details, and associated filters.
    """
    # attacks = attacks.split(",")

    attack_config_objects = []

    FILTER_CLASSES = {
        "IsGetProductDetailsActionFilter": IsGetProductDetailsActionFilter,
        "IsRespondActionFilter": IsRespondActionFilter,
    }

    for component_dict, attack in zip(attackable_components, attacks):
        # Extract filter class
        filter_class_name = component_dict.pop("filter")
        filter_instance = FILTER_CLASSES[filter_class_name]()

        # Build the attackable component object
        attackable_component_object = {
            "attackable_component": component_dict["attackable_component"],
            "filter": filter_instance,
        }

        # Fetch the attack definition
        attack_object = fetch_attack(attack, domain, task_index)

        # Construct the AttackConfig
        attack_config_objects.append(
            AttackConfig(
                attackable_component=attackable_component_object[
                    "attackable_component"
                ],
                attack=attack_object["attack"],
                filter=attackable_component_object["filter"],
                success_filter=attack_object["success_filter"],
            )
        )

    return attack_config_objects


def agent_factory(tools_info: List[Dict[str, Any]], wiki, args: dict) -> Agent:
    """
    Factory function to create an agent instance based on the specified strategy.

    Args:
        tools_info (List[Dict[str, Any]]): A list of dictionaries containing information about the tools available to the agent.
        wiki: A reference to the wiki or knowledge base used by the agent.
        args: Parsed command-line arguments containing configuration options for the agent.

    Returns:
        Agent: An instance of the appropriate agent class based on the specified strategy.
    """
    if args["agent_strategy"] == "tool-calling":
        # native tool calling
        from tau_bench.agents.tool_calling_agent import ToolCallingAgent

        return ToolCallingAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=args["model"],
            provider=args["model_provider"],
            temperature=args["temperature"],
        )
    elif args["agent_strategy"] == "act":
        # `act` from https://arxiv.org/abs/2210.03629
        from tau_bench.agents.chat_react_agent import ChatReActAgent

        return ChatReActAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=args["model"],
            provider=args["model_provider"],
            use_reasoning=False,
            temperature=args["temperature"],
        )
    elif args["agent_strategy"] == "react":
        # `react` from https://arxiv.org/abs/2210.03629
        from tau_bench.agents.chat_react_agent import ChatReActAgent

        return ChatReActAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=args["model"],
            provider=args["model_provider"],
            use_reasoning=True,
            temperature=args["temperature"],
        )
    elif args["agent_strategy"] == "few-shot":
        from tau_bench.agents.few_shot_agent import FewShotToolCallingAgent

        with open(args["few_shot_displays_path"], "r") as f:
            few_shot_displays = [json.loads(line)["messages_display"] for line in f]

        return FewShotToolCallingAgent(
            tools_info=tools_info,
            wiki=wiki,
            model=args["model"],
            provider=args["model_provider"],
            few_shot_displays=few_shot_displays,
            temperature=args["temperature"],
        )
    else:
        raise ValueError(f"Unknown agent strategy: {args['agent_strategy']}")


def setup_defense(args):
    """
    Configures and sets up a defense mechanism for safe completion handling.

    Args:
        args: Contains configuration parameters for the trial.
    """
    from doomarena.core.agent_defenses.safe_completion_gateway import (
        SafeCompletionWrapper,
    )
    import litellm

    if args["safety_check_model"] == "llamaguard":
        from doomarena.core.agent_defenses.llamaguard import LlamaGuardSafetyCheck

        safety_check = LlamaGuardSafetyCheck

    elif args["safety_check_model"] == "llamaguardapi":
        from doomarena.core.agent_defenses.llamaguard_api import (
            LlamaGuardSafetyCheckAPI,
        )

        os.environ["groq_api_key"] = "GROQ_API_KEY"
        safety_check = LlamaGuardSafetyCheckAPI

    elif args["safety_check_model"] == "llmjudge":
        from doomarena.core.agent_defenses.llmjudge import (
            LLMJudgeSafetyCheck,
        )

        safety_check = LLMJudgeSafetyCheck

    wrapper = SafeCompletionWrapper(safety_check, args["abort"])
    litellm.completion = wrapper.safe_completion


def calculate_steps_per_task_completion(envRunResultDict):
    """
    Calculates the total number of steps taken by the assistant to complete a task.

    Args:
        envRunResultDict (dict): A dictionary containing the task execution details
    """
    envRunResultDict["steps"] = sum(
        1 for message in envRunResultDict["traj"] if message["role"] == "assistant"
    )


def is_task_successful(reward: float) -> bool:
    """
    Determines if a task is successful based on the given reward value.

    Args:
        reward (float): The reward value to evaluate.

    Returns:
        bool: True if the reward is within the acceptable range, False otherwise.
    """
    return (1 - 1e-6) <= reward <= (1 + 1e-6)


def average_trial_results(args, all_task_results):
    """
    Combines and averages attack success rates, rewards, and other metrics across multiple trials for each task.

    Args:
        args: Contains configuration parameters for the trial.
        all_task_results (dict): A dictionary where keys are task IDs and values are lists of trial results.

    Returns:
        list: A list of dictionaries, each representing the averaged results for a task.
    """
    # Combine and average attack success and rewards by task_id across all trials
    averaged_data = []
    for task_id, task_trials in all_task_results.items():
        combined_data = {
            "task_id": task_id,
            "reward": [],
            "attack_success": {},
            "steps": [],
            "common_attributes": {},
        }
        for entry in task_trials:
            if not combined_data["common_attributes"]:
                combined_data["common_attributes"] = {
                    key: entry[key]
                    for key in entry
                    if key
                    not in [
                        "reward",
                        "attack_success",
                        "task_id",
                        "info",
                        "traj",
                        "trial",
                        "steps",
                    ]
                }

            attack_successes = entry.get("attack_success", [])

            # Ensure attack_success is always a list before appending
            if not isinstance(combined_data["attack_success"], dict):
                combined_data["attack_success"] = {}

            combined_data["reward"].append(
                1 if is_task_successful(entry["reward"]) else 0
            )

            combined_data["steps"].append(entry["steps"])

            for idx, value in enumerate(attack_successes):
                if idx not in combined_data["attack_success"]:
                    combined_data["attack_success"][idx] = []
                combined_data["attack_success"][idx].append(value)

        if len(combined_data["attack_success"]) == 3:
            # For combined attacks, compute reward and attack success for cases where both attacks executed
            success_vals = list(combined_data["attack_success"].values())
            attack_success_list = [
                max(success_vals[0][i], success_vals[2][i])
                for i in range(len(success_vals[0]))
                if success_vals[1][i]
            ]
            rewards = [
                combined_data["reward"][i]
                for i in range(len(success_vals[0]))
                if success_vals[1][i]
            ]
        else:
            attack_success_list = [
                num
                for value in combined_data["attack_success"].values()
                for num in value
            ]
            rewards = combined_data["reward"]

        avg_reward = sum(rewards) / len(rewards) if rewards else 0.0

        avg_attack_success = (
            sum(attack_success_list) / len(attack_success_list)
            if attack_success_list
            else 0.0
        )

        averaged_task_data = {
            "task_id": task_id,
            "runs": len(task_trials),
            "avg_reward": avg_reward,
            "avg_attack_success": avg_attack_success,
            "reward": combined_data["reward"],
            "attack_success": [
                subset for subset in combined_data["attack_success"].values()
            ],
            "steps": combined_data["steps"],
            **combined_data["common_attributes"],
        }

        # Load cluster labels
        if args["env"] == "retail":
            cluster_file_path = (
                Path(__file__).parent.parent / "data" / "retail_classification.json"
            )
        elif args["env"] == "airline":
            cluster_file_path = (
                Path(__file__).parent.parent / "data" / "airline_classification.json"
            )
        else:
            raise ValueError(f"Unknown env: {args['env']}")

        with open(cluster_file_path, "r") as f:
            cluster_labels = json.load(f)

        # Find the cluster labels for the current task_id
        task_cluster_info = next(
            (item for item in cluster_labels if (item["task_id"] + 1) == int(task_id)),
            None,
        )
        if task_cluster_info:
            averaged_task_data["cluster_1"] = task_cluster_info["cluster_1"]
            averaged_task_data["cluster_2"] = task_cluster_info["cluster_2"]
        else:
            averaged_task_data["cluster_1"] = "Unknown"
            averaged_task_data["cluster_2"] = "Unknown"

        averaged_data.append(averaged_task_data)

    return averaged_data


def run_trial(agent, args, trial_num: int, task_id: int) -> EnvRunResult:
    """
    Executes a single trial of an agent solving a task in an isolated environment.

    Args:
        agent: The agent instance responsible for solving the task.
        args: Contains configuration parameters for the trial.
        trial_num (int): The current trial number.
        task_id (int): The unique identifier for the task being solved.
    Returns:
        EnvRunResult: An object containing the results of the trial.
    """
    isolated_env = get_env(
        args["env"],
        user_strategy=args["user_strategy"],
        user_model=args["user_model"],
        task_split=args["task_split"],
        user_provider=args["user_model_provider"],
        task_index=task_id,
    )
    if args["add_attack"] == "Yes":
        isolated_env = get_adv_env(
            isolated_env,
            args["env"],
            args["attack_gateway"],
            args["attackable_components"],
            args["attacks"],
            task_id,
            None,
        )

    try:
        res = agent.solve(
            env=isolated_env,
            task_index=task_id,
        )
        result = EnvRunResult(
            task_id=task_id,
            reward=res.reward,
            info=res.info,
            traj=res.messages,
            trial=trial_num + 1,
        )
        result = result.model_dump()
        if args["add_attack"] == "Yes":
            if any(
                attack["name"] == "malicious_user_retail_attack"
                for attack in args["attacks"]
            ):
                isolated_env.attack_success(result_object=result)
            else:
                isolated_env.attack_success()
            attack_metrics = isolated_env.attack_metrics
            attack_metrics["attackable_components"] = args["attackable_components"]
            attack_metrics["attacks"] = args["attacks"]
            result = result | attack_metrics
    except Exception as e:
        result = EnvRunResult(
            task_id=task_id,
            reward=0.0,
            info={"error": str(e), "traceback": traceback.format_exc()},
            traj=[],
            trial=trial_num + 1,
        )
        if args["save_results"]:
            result = result.model_dump()
    print(
        "✅" if result["reward"] == 1 else "❌",
        f"task_id={task_id}",
        result["info"],
    )
    print("-----")
    calculate_steps_per_task_completion(result)
    return result


def run_trials(
    args: dict[str, Any],
) -> List[EnvRunResult]:
    """
    Executes the Taubench attack pipeline based on the provided arguments.

    Args:
        args: Parsed command-line arguments containing configuration options for the trial.

    Returns:
        List[EnvRunResult]: A list of averaged results across all tasks and trials.
    """
    if args["add_defense"] == "Yes":
        setup_defense(args)

    print(f"Loading user with strategy: {args['user_strategy']}")

    env = get_env(
        args["env"],
        user_strategy=args["user_strategy"],
        user_model=args["user_model"],
        user_provider=args["user_model_provider"],
        task_split=args["task_split"],
    )

    agent = agent_factory(
        tools_info=env.tools_info,
        wiki=env.wiki,
        args=args,
    )

    end_index = (
        len(env.tasks)
        if args["end_index"] == -1
        else min(args["end_index"], len(env.tasks))
    )

    if args["save_results"]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_output_dir = os.path.join(
            args["log_dir"], args["env"], f"taubench_run_{timestamp}"
        )
        os.makedirs(base_output_dir, exist_ok=True)

    all_results = {}

    if args["task_ids"] and len(args["task_ids"]) > 0:
        task_idxs = args["task_ids"]
    else:
        task_idxs = list(range(args["start_index"], end_index))

    if args["shuffle"]:
        random.shuffle(task_idxs)

    for idx in task_idxs:
        if args["save_results"]:
            task_results_dir = os.path.join(base_output_dir, f"task_{idx}")
            os.makedirs(task_results_dir, exist_ok=True)

        task_results = []

        for i in range(args["num_trials"]):
            file_output_str = (
                f"trial-{i+1}_{args['agent_strategy']}-{args['model'].split('/')[-1]}-{args['temperature']}_user-{args['user_strategy']}_taskid-{idx}"
                if args["user_strategy"] == "human"
                else f"trial-{i+1}_{args['agent_strategy']}-{args['model'].split('/')[-1]}-{args['temperature']}_user-{args['user_model'].split('/')[-1]}-{args['user_strategy']}_taskid-{idx}"
            )

            if args["save_results"]:
                results_file = os.path.join(
                    task_results_dir, f"{file_output_str}_results.json"
                )

            print(f"\n=== Running Task {idx} Trial {i + 1}/{args['num_trials']} ===")

            if args["save_results"]:
                print(f"Results will be saved to: {results_file}")

            result = run_trial(agent, args, idx, i)
            result["add_attack"] = args["add_attack"]
            result["agent_model"] = args["model"]
            result["agent_strategy"] = args["agent_strategy"]
            result["user_strategy"] = args["user_strategy"]
            if args["user_strategy"] != "human":
                result["user_model"] = args["user_model"]

            if args["save_results"]:
                with open(results_file, "w") as f:
                    json.dump([result], f, indent=2)

                print(f"Trial results for task {idx} saved to {results_file}.")

            task_results.append(result)

        all_results[idx] = task_results

    avg_all_results = average_trial_results(args, all_results)

    if args["save_results"]:
        with open(f"{base_output_dir}/aggregate_results.json", "w") as f:
            json.dump(avg_all_results, f, indent=2)

        print(
            f"\nAveraged results across trials saved at: {base_output_dir}/aggregate_results.json\n"
        )

    return avg_all_results


def run_tau_bench_attack(config_args, save_results=False):
    """
    Executes the TauBench attack simulation based on the provided configuration arguments.

    Args:
        config_args (dict): A dictionary containing configuration parameters for the attack.
            Supported keys include:
            - num_trials (int): Number of trials to run. Default is 1.
            - env (str): Environment for the attack. Must be one of ["retail", "airline"]. Default is "retail".
            - add_attack (str): Whether to add an attack. Default is "No".
            - user_model (str): User model to use. Default is "gpt-4o".
            - agent_strategy (str): Strategy for the agent. Must be one of ["tool-calling", "act", "react", "few-shot"]. Default is "tool-calling".
            - temperature (float): Temperature for randomness in model responses. Default is 0.0.
            - task_split (str): Task split to use. Must be one of ["train", "test", "dev"]. Default is "test".
            - start_index (int): Starting index for tasks. Default is 0.
            - end_index (int): Ending index for tasks. Default is -1 (process all tasks).
            - log_dir (str): Directory to save logs. Default is "results/taubench".
            - max_concurrency (int): Maximum number of concurrent tasks. Default is 1.
            - seed (int): Random seed for reproducibility. Default is 10.
            - shuffle (int): Whether to shuffle tasks. Default is 0.
            - add_defense (str): Whether to add a defense mechanism. Default is "No".
            - safety_check_model (str): Model for safety checks. Must be one of ["llamaguard", "llamaguardapi", "llmjudge"]. Default is "llmjudge".
            - abort (bool): Whether to abort on critical errors. Default is True.
            - model_provider (str): Provider for the model. Must be in `provider_list`.
            - user_model_provider (str): Provider for the user model. Must be in `provider_list`.
            - user_strategy (str): Strategy for the user. Must be a valid value from `UserStrategy`.
            - attack_gateway (str): Gateway for the attack. Must be in `ATTACK_GATEWAY_REGISTRY`.

        save_results (bool, optional): Whether to save the results to the log directory. Default is False.

    Raises:
        ValueError: If any of the provided configuration values are invalid.

    Returns:
        Any: The result of the trials executed by the `run_trials` function.
    """
    # Default values
    defaults = {
        "num_trials": 1,
        "env": "retail",
        "add_attack": "No",
        "user_model": "gpt-4o",
        "agent_strategy": "tool-calling",
        "temperature": 0.0,
        "task_split": "test",
        "start_index": 0,
        "end_index": -1,
        "log_dir": "results/taubench",
        "max_concurrency": 1,
        "seed": 10,
        "shuffle": 0,
        "add_defense": "No",
        "safety_check_model": "llmjudge",
        "abort": True,
    }

    # Merge defaults with config
    for key, val in defaults.items():
        config_args.setdefault(key, val)

    # Manual validations
    if config_args["env"] not in ["retail", "airline"]:
        raise ValueError(f"Invalid env: {config_args['env']}")

    if config_args.get("model_provider") not in provider_list:
        raise ValueError(f"Invalid model_provider: {config_args.get('model_provider')}")

    if config_args.get("user_model_provider") not in provider_list:
        raise ValueError(
            f"Invalid user_model_provider: {config_args.get('user_model_provider')}"
        )

    if config_args["agent_strategy"] not in [
        "tool-calling",
        "act",
        "react",
        "few-shot",
    ]:
        raise ValueError(f"Invalid agent_strategy: {config_args['agent_strategy']}")

    if config_args["task_split"] not in ["train", "test", "dev"]:
        raise ValueError(f"Invalid task_split: {config_args['task_split']}")

    if config_args["user_strategy"] not in [item.value for item in UserStrategy]:
        raise ValueError(f"Invalid user_strategy: {config_args['user_strategy']}")

    if config_args["attack_gateway"] not in ATTACK_GATEWAY_REGISTRY:
        raise ValueError(f"Invalid attack_gateway: {config_args['attack_gateway']}")

    if config_args["safety_check_model"] not in [
        "llamaguard",
        "llamaguardapi",
        "llmjudge",
    ]:
        raise ValueError(
            f"Invalid safety_check_model: {config_args['safety_check_model']}"
        )

    if not os.path.exists(config_args["log_dir"]) and save_results:
        os.makedirs(config_args["log_dir"])

    if "save_results" not in config_args:
        config_args["save_results"] = save_results

    random.seed(config_args["seed"])
    print(config_args)

    result = run_trials(args=config_args)
    return result


def main(args_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="Path to YAML config file")
    args, _ = parser.parse_known_args(args_list)

    if args.config:
        with open(args.config, "r") as f:
            config_args = yaml.safe_load(f)
    else:
        raise ValueError("YAML config must be provided using --config")
    return run_tau_bench_attack(config_args)


if __name__ == "__main__":
    main()
