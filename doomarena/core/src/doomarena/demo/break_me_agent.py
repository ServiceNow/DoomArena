import copy
import json
import logging
from types import MethodType
from typing import Literal
from agentlab.agents.agent_args import AgentArgs
from agentlab.agents.generic_agent import (
    AGENT_LLAMA3_70B,
    AGENT_LLAMA31_70B,
    RANDOM_SEARCH_AGENT,
    AGENT_4o,
    AGENT_4o_MINI,
)
import bgym


class BreakMeAgentArgs(AgentArgs):
    """
    This agent is designed to break when the trigger is detected.
    Construct it from a regular AgentArgs.
    The Agent's get_action() will be patched with hard-coded action when trigger is detected in observation.
    If no triggers are detected, the original action will be returned.

    trigger_to_action: dict[str, str]
        Maps triggers to hard-coded actions.
    """

    def __init__(
        self,
        agent_args: AgentArgs,
        trigger_to_action: dict[str | Literal["*"], str],
    ):
        self.agent_args = agent_args
        self.trigger_to_action = trigger_to_action
        self.agent_name = "BreakMeAgent"

    def set_benchmark(self, benchmark: bgym.Benchmark, demo_mode):
        """Set up trigger_to_action depending on action if required."""
        self.agent_args.set_benchmark(benchmark, demo_mode)

        # if self.trigger_to_action == "auto":
        #     raise Exception("Implement benchmark specific shortcuts")
        #     if benchmark.name.startswith("miniwob"):
        #         self.trigger_to_action = {"break_me": "goto()"}
        #     else:
        #         self.trigger_to_action = {"break_me": "click()"}

    def make_agent(self):
        agent = self.agent_args.make_agent()

        original_get_action = agent.get_action

        def get_action_wrapper(wrapped_self, obs):
            assert (
                "dom_object" in obs or "axtree_object" in obs
            ), "Observation must contain dom_object or axtree_object"
            obs_str = ""
            if "dom_object" in obs:
                obs_str += json.dumps(obs["dom_object"]).lower() + "|"
            if "axtree_object" in obs:
                obs_str += json.dumps(obs["axtree_object"]).lower() + "|"

            for trigger, action in self.trigger_to_action.items():
                if trigger in obs_str or trigger == "*":
                    logging.debug(
                        f"Trigger detected: {trigger}. Returning hard-coded action: {action}"
                    )
                    return action, {}
            return original_get_action(obs)

        agent.get_action = MethodType(get_action_wrapper, agent)

        # Patch agent's get_action to intercept action when trigger is detected in environment
        return agent

    @property
    def flags(self):
        return self.agent_args.flags


BREAKME_AGENT_4o_MINI = BreakMeAgentArgs(
    AGENT_4o_MINI,
    trigger_to_action={
        "mandatory": 'goto("http://localhost:1234/register_start?obs=BreakMeHardCodedObs")'
    },
)

ALWAYSBREAK_AGENT_4o_MINI = BreakMeAgentArgs(
    AGENT_4o_MINI,
    trigger_to_action={
        "*": 'goto("http://localhost:1234/register_start?obs=BreakMeHardCodedObs")'
    },
)
