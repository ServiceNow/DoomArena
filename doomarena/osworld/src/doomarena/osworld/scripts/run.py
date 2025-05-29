"""Script to run end-to-end evaluation on the benchmark.
Utils and basic architecture credit to https://github.com/web-arena-x/webarena/blob/main/run.py.
"""

import argparse
import datetime
import json
import logging
import os
import sys
import yaml
from tqdm import tqdm
from doomarena.osworld.attack_gateway import OSWorldAttackGateway
from doomarena.core.attack_gateways.register_attack_gateway import (
    ATTACK_GATEWAY_REGISTRY,
)
from doomarena.core.attack_gateways.get_attack_gateway import (
    get_attack_gateway,
)
from doomarena.core.attack_config.attack_config import AttackConfig
from doomarena.core.filters.always_true_filter import AlwaysTrueFilter
from doomarena.osworld.success_filters.popup_click_success_filter import (
    PopupClickSuccessFilter,
)
from doomarena.core.attacks import get_attacks

from doomarena.osworld import lib_run_single
from doomarena.osworld.mm_agents.agent import PromptAgent
from desktop_env.desktop_env import DesktopEnv

#  Logger Configs {{{ #
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

datetime_str: str = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")

file_handler = logging.FileHandler(
    os.path.join("logs", "normal-{:}.log".format(datetime_str)), encoding="utf-8"
)
debug_handler = logging.FileHandler(
    os.path.join("logs", "debug-{:}.log".format(datetime_str)), encoding="utf-8"
)
stdout_handler = logging.StreamHandler(sys.stdout)
sdebug_handler = logging.FileHandler(
    os.path.join("logs", "sdebug-{:}.log".format(datetime_str)), encoding="utf-8"
)

file_handler.setLevel(logging.INFO)
debug_handler.setLevel(logging.DEBUG)
stdout_handler.setLevel(logging.INFO)
sdebug_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="\x1b[1;33m[%(asctime)s \x1b[31m%(levelname)s \x1b[32m%(module)s/%(lineno)d-%(processName)s\x1b[1;33m] \x1b[0m%(message)s"
)
file_handler.setFormatter(formatter)
debug_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
sdebug_handler.setFormatter(formatter)

stdout_handler.addFilter(logging.Filter("desktopenv"))
sdebug_handler.addFilter(logging.Filter("desktopenv"))

logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(stdout_handler)
logger.addHandler(sdebug_handler)
#  }}} Logger Configs #

logger = logging.getLogger("desktopenv.experiment")


def config():
    parser = argparse.ArgumentParser(
        description="Run end-to-end evaluation on the benchmark"
    )

    # environment config
    parser.add_argument(
        "--config_file",
        type=str,
        required=True,
        help="Path to the YAML configuration file",
    )
    args = parser.parse_args()

    if not os.path.exists(args.config_file):
        raise FileNotFoundError(f"Config file {args.config_file} not found.")

    with open(args.config_file, "r") as f:
        config_args = yaml.safe_load(f)

    defaults = {
        "path_to_vm": None,
        "add_attack": "No",
        "headless": False,
        "action_space": "pyautogui",
        "observation_type": "a11y_tree",
        "screen_width": 1920,
        "screen_height": 1080,
        "sleep_after_execution": 0.0,
        "max_steps": 15,
        "max_trajectory_length": 3,
        "test_config_base_dir": "evaluation_examples",
        "model": "gpt-4o",
        "temperature": 1.0,
        "top_p": 0.9,
        "max_tokens": 1500,
        "stop_token": None,
        "domain": "all",
        "test_all_meta_path": "evaluation_examples/test_all.json",
        "result_dir": "./results",
        "attack_gateway": None,
        "save_results": True,
    }

    # Apply defaults
    for key, val in defaults.items():
        config_args.setdefault(key, val)

    # Manual validations
    valid_observations = ["screenshot", "a11y_tree", "screenshot_a11y_tree", "som"]
    if config_args["observation_type"] not in valid_observations:
        raise ValueError(f"Invalid observation_type: {config_args['observation_type']}")

    if (
        config_args["attack_gateway"] is not None
        and config_args["attack_gateway"] not in ATTACK_GATEWAY_REGISTRY
    ):
        raise ValueError(f"Invalid attack_gateway: {config_args['attack_gateway']}")

    if not os.path.exists(config_args["result_dir"]) and config_args["save_results"]:
        os.makedirs(config_args["result_dir"])

    print("Final config:", config_args)

    return config_args


def fetch_attack(attack_config):
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
    attack_args = {
        "name": attack_config["type"],
        "injection_str": attack_config["injection_str"],
    }

    SUCCESS_FILTER_CLASSES = {
        "popup_click_success_filter": PopupClickSuccessFilter,
    }

    # initialize success filters
    success_filter_cls = SUCCESS_FILTER_CLASSES[attack_config["success_filter"]]
    success_filter_args = attack_config.get("success_filter_args", {})
    success_filter = success_filter_cls(**success_filter_args)

    return {
        "attack": get_attacks(**attack_args),
        "success_filter": success_filter,
    }


def fetch_attack_configs(attackable_components: list, attacks: list):
    """
    Fetches and constructs attack configuration objects based on the provided attackable components and attacks.

    Args:
        attackable_components (list): A list of attackable components.
        attacks (list): A list of attacks.

    Returns:
        list: A list of `AttackConfig` objects, each containing the attackable component, attack details, and associated filters.
    """
    assert len(attackable_components) == len(attacks), (
        "The number of attackable components must match the number of attacks."
    )

    attack_config_objects = []
    FILTER_CLASSES = {
        "always_true": AlwaysTrueFilter,
    }

    for component_dict, attack in zip(attackable_components, attacks):
        # Build the attackable component object
        filter_class_name = component_dict.pop("filter")
        filter_instance = FILTER_CLASSES[filter_class_name]()

        attackable_component_object = {
            "attackable_component": component_dict["attackable_component"],
            "filter": filter_instance,
        }

        # Fetch the attack definition
        attack_object = fetch_attack(attack)

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


def test(config_args, test_all_meta: dict, save_results: bool = True) -> None:
    scores = []
    attack_scores = []
    stealth_scores = []
    max_steps = config_args["max_steps"]

    # log args
    logger.info("Args: %s", config_args)

    agent = PromptAgent(
        model=config_args["model"],
        max_tokens=config_args["max_tokens"],
        top_p=config_args["top_p"],
        temperature=config_args["temperature"],
        action_space=config_args["action_space"],
        observation_type=config_args["observation_type"],
        max_trajectory_length=config_args["max_trajectory_length"],
    )

    attack_configs = fetch_attack_configs(
        config_args["attackable_components"], config_args["attacks"]
    )

    if config_args["add_attack"] == "Yes":
        env = get_attack_gateway(
            name=config_args["attack_gateway"],
            cache_dir="../OSWorld/cache",
            attack_configs=attack_configs,
            path_to_vm=config_args["path_to_vm"],
            action_space=agent.action_space,
            screen_size=(config_args["screen_width"], config_args["screen_height"]),
            headless=config_args["headless"],
            os_type="Ubuntu",
            require_a11y_tree=config_args["observation_type"]
            in ["a11y_tree", "screenshot_a11y_tree", "som"],
        )
    else:
        env = DesktopEnv(
            path_to_vm=config_args["path_to_vm"],
            cache_dir="../OSWorld/cache",
            action_space=agent.action_space,
            screen_size=(config_args["screen_width"], config_args["screen_height"]),
            headless=config_args["headless"],
            os_type="Ubuntu",
            require_a11y_tree=config_args["observation_type"]
            in ["a11y_tree", "screenshot_a11y_tree", "som"],
        )

    for domain in tqdm(test_all_meta, desc="Domain"):
        for example_id in tqdm(test_all_meta[domain], desc="Example", leave=False):
            config_file = os.path.join(
                config_args["test_config_base_dir"],
                f"examples/{domain}/{example_id}.json",
            )
            with open(config_file, "r", encoding="utf-8") as f:
                example = json.load(f)

            logger.info(f"[Domain]: {domain}")
            logger.info(f"[Example ID]: {example_id}")

            instruction = example["instruction"]

            logger.info(f"[Instruction]: {instruction}")
            # wandb each example config settings
            config_args["instruction"] = instruction
            config_args["start_time"] = datetime.datetime.now().strftime(
                "%Y:%m:%d-%H:%M:%S"
            )
            # run.config.update(config_args)

            example_result_dir = os.path.join(
                config_args["result_dir"],
                config_args["action_space"],
                config_args["observation_type"],
                config_args["model"],
                domain,
                example_id,
            )
            os.makedirs(example_result_dir, exist_ok=True)
            # example start running
            try:
                from argparse import Namespace

                args = Namespace(**config_args)
                lib_run_single.run_single_example(
                    agent,
                    env,
                    example,
                    max_steps,
                    instruction,
                    args,
                    example_result_dir,
                    scores,
                )

                if config_args["add_attack"] == "Yes":
                    env.attack_success()
                    attack_success_val = env.attack_success_
                    print("Attack success value: ", attack_success_val)
                    attack_scores.append(attack_success_val)
                    stealth_scores.append(scores[-1] > 0 and attack_success_val > 0)

                    logger.info(f"Average Attack score: {sum(attack_scores) / len(attack_scores)} (over {len(attack_scores)})")
                    logger.info(
                        f"Average Stealth score: {sum(stealth_scores) / len(stealth_scores)} (over {len(stealth_scores)})"
                    )

                logger.info(f"Average Task score: {sum(scores) / len(scores)}")

            except Exception as e:
                logger.error(f"Exception in {domain}/{example_id}: {e}")
                env.controller.end_recording(
                    os.path.join(example_result_dir, "recording.mp4")
                )
                with open(os.path.join(example_result_dir, "traj.jsonl"), "a") as f:
                    f.write(
                        json.dumps(
                            {"Error": f"Time limit exceeded in {domain}/{example_id}"}
                        )
                    )
                    f.write("\n")

    env.close()
    logger.info(f"Total examples: {len(scores)}")
    logger.info(f"Average Task score: {sum(scores) / len(scores)}")
    if config_args["add_attack"] == "Yes":
        logger.info(f"Average Attack score: {sum(attack_scores) / len(attack_scores)} (over {len(attack_scores)})")
        logger.info(
            f"Average Stealth score: {sum(stealth_scores) / len(stealth_scores)} (over {len(stealth_scores)})"
        )


def get_unfinished(
    action_space, use_model, observation_type, result_dir, total_file_json
):
    target_dir = os.path.join(result_dir, action_space, observation_type, use_model)

    if not os.path.exists(target_dir):
        return total_file_json

    finished = {}
    for domain in os.listdir(target_dir):
        finished[domain] = []
        domain_path = os.path.join(target_dir, domain)
        if os.path.isdir(domain_path):
            for example_id in os.listdir(domain_path):
                if example_id == "onboard":
                    continue
                example_path = os.path.join(domain_path, example_id)
                if os.path.isdir(example_path):
                    if "result.txt" not in os.listdir(example_path):
                        # empty all files under example_id
                        for file in os.listdir(example_path):
                            os.remove(os.path.join(example_path, file))
                    else:
                        finished[domain].append(example_id)

    if not finished:
        return total_file_json

    for domain, examples in finished.items():
        if domain in total_file_json:
            total_file_json[domain] = [
                x for x in total_file_json[domain] if x not in examples
            ]

    return total_file_json


def get_result(action_space, use_model, observation_type, result_dir, total_file_json):
    target_dir = os.path.join(result_dir, action_space, observation_type, use_model)
    if not os.path.exists(target_dir):
        print("New experiment, no result yet.")
        return None

    all_result = []

    for domain in os.listdir(target_dir):
        domain_path = os.path.join(target_dir, domain)
        if os.path.isdir(domain_path):
            for example_id in os.listdir(domain_path):
                example_path = os.path.join(domain_path, example_id)
                if os.path.isdir(example_path):
                    if "result.txt" in os.listdir(example_path):
                        # empty all files under example_id
                        try:
                            all_result.append(
                                float(
                                    open(
                                        os.path.join(example_path, "result.txt"), "r"
                                    ).read()
                                )
                            )
                        except:
                            all_result.append(0.0)

    if not all_result:
        print("New experiment, no result yet.")
        return None
    else:
        print("Current Success Rate:", sum(all_result) / len(all_result) * 100, "%", f"({len(all_result)} examples)")
        return all_result


if __name__ == "__main__":
    assert os.path.exists("../OSWorld"), "Please clone OSWorld repository next to DoomArena. Run this script from the root of DoomArena."
    assert os.path.exists("../OSWorld/cache"), "Please download the cache from https://drive.google.com/file/d/1XlEy49otYDyBlA3O9NbR0BpPfr2TXgaD/view and put it in ../OSWorld/cache"

    ####### The complete version of the list of examples #######
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    args = config()

    with open(args["test_all_meta_path"], "r", encoding="utf-8") as f:
        test_all_meta = json.load(f)

    if args["domain"] != "all":
        test_all_meta = {args["domain"]: test_all_meta[args["domain"]]}

    test_file_list = get_unfinished(
        args["action_space"],
        args["model"],
        args["observation_type"],
        args["result_dir"],
        test_all_meta,
    )
    left_info = ""
    for domain in test_file_list:
        left_info += f"{domain}: {len(test_file_list[domain])}\n"
    logger.info(f"Left tasks:\n{left_info}")

    get_result(
        args["action_space"],
        args["model"],
        args["observation_type"],
        args["result_dir"],
        test_all_meta,
    )

    test(args, test_file_list)
