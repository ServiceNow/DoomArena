"""
A bunch of utilities for running experiments with the LLMail agent.
"""

from abc import abstractmethod
from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Callable, Literal
from doomarena.core.success_filters import SuccessFilter
from pydantic import BaseModel

from tapeagents.dialog_tape import AssistantStep, UserStep
from tapeagents.orchestrator import main_loop
from tapeagents.llms import LLM, LLMStream, TrainableLLM

from .types import (
    Email,
    LLMailTape,
    ListedEmailsResults,
    Results,
    SendEmailResults,
    MailInjectExperiment,
)
from .environment import LLMailEnvironment
from .environment.assets import GPT4o_GENERATED_EMAILS_V1
from .agent import GENERIC_ASSISTANT_MESSAGE, LLMailAgent

logger = logging.getLogger(__name__)


def create_results_folder(base_path: Path = None) -> Path:
    """
    Generates a path like:
        <base_path>/results/YYYY-MM-DD/HH-MM-SS
    and creates the folder (including intermediate directories).

    By default, base_path is the current working directory.

    Returns:
        Path: The full path to the new folder.
    """
    if base_path is None:
        base_path = Path.cwd()

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")

    results_path = base_path / "results" / date_str / time_str
    results_path.mkdir(parents=True, exist_ok=True)

    return results_path


def prepare_test_case_args(
    test_case: MailInjectExperiment,  # Replace with your actual test_case type, e.g. MailInjectExperiment
) -> tuple[LLMailAgent, LLMailEnvironment, LLMailTape]:

    assert test_case.llm, "Test case must have an LLM"
    llm_name: str = (
        test_case.llm.model_name if isinstance(test_case.llm, LLM) else test_case.llm
    )
    user_as_system_turn = "phi" in llm_name.lower()
    logger.info(f"Selected user_as_system_turn: {user_as_system_turn}")

    # Create the LLMailAgent
    # Change with LLMailAgentSpolight
    kind_spotlighting = ""
    for defense in test_case.defenses:
        if defense == "spotlighting_delimiters":
            kind_spotlighting = "delimiters"
        elif defense == "spotlighting_datamarking":
            kind_spotlighting = "datamarking"
        elif defense == "spotlighting_base64":
            kind_spotlighting = "base64"
        elif "spotlighting" in defense:
            raise ValueError(f"Unknown spotlighting defense: {defense}")

    agent = LLMailAgent.create(
        llm=test_case.llm,
        templates={},
        user_as_system_turn=user_as_system_turn,
        kind_spotlighting=kind_spotlighting,
    )

    # Create the LLMailEnvironment
    env = LLMailEnvironment(emails=test_case.emails)

    # Create the LLMailTape
    start_tape = LLMailTape(
        steps=[
            AssistantStep(content=GENERIC_ASSISTANT_MESSAGE),
            UserStep(content=test_case.user_message),
        ]
    )

    return agent, env, start_tape


def run_mailinject_experiment(test_case: MailInjectExperiment) -> MailInjectExperiment:

    agent, env, start_tape = prepare_test_case_args(test_case)

    final_tape = main_loop(
        agent, start_tape, env, max_loops=test_case.max_loops
    ).get_final_tape()
    logger.info(final_tape)

    # apply success filter
    results = test_case.success_filter(final_tape)
    test_case_with_results = test_case.model_copy(deep=True)
    test_case_with_results.results = results
    test_case_with_results.final_tape = final_tape.model_copy(deep=True)
    test_case_with_results.llm.tokenizer = None  # can't serialize tokenizer

    return test_case_with_results
