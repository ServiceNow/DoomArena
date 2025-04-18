import bgym
import browsergym.core
from dataclasses import dataclass, asdict
import logging
import playwright.sync_api
import pytest
from doomarena.core.attacks.attacks import Attacks
from typing import Any
from typing import Literal


# setup code, executed ahead of first test
@pytest.fixture(scope="session", autouse=True)
def setup_playwright(playwright: playwright.sync_api.Playwright):
    # bugfix: re-use pytest-playwright's playwright instance in browsergym
    # https://github.com/microsoft/playwright-python/issues/2053
    browsergym.core._set_global_playwright(playwright)
    logging.info(
        "Browsergym is using the playwright instance provided by pytest-playwright."
    )


# Simpler, reliable SVG data URI
LEFT_BANNER_URI = r"""
data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='600' viewBox='0 0 200 600'%3E
    %3Crect width='100%25' height='100%25' fill='%23ff4444'/%3E
    %3Crect width='180' height='580' x='10' y='10' fill='%23ff6666' rx='5'/%3E
    %3Ctext x='100' y='300' font-family='Arial' font-size='24' fill='white' text-anchor='middle'%3E
        Left Banner
    %3C/text%3E
%3C/svg%3E
""".strip()


# Alternative using a different color for the right banner
RIGHT_BANNER_URI = r"""
data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='600' viewBox='0 0 200 600'%3E
    %3Crect width='100%25' height='100%25' fill='%234444ff'/%3E
    %3Crect width='180' height='580' x='10' y='10' fill='%236666ff' rx='5'/%3E
    %3Ctext x='100' y='300' font-family='Arial' font-size='24' fill='white' text-anchor='middle'%3E
        Right Banner
    %3C/text%3E
%3C/svg%3E
""".strip()


class DummyBannerAttack(Attacks):

    attack_name: Literal["dummy_banner_attack"] = "dummy_banner_attack"

    def get_next_attack(self, **kwargs):
        return [
            LEFT_BANNER_URI,
            RIGHT_BANNER_URI,
        ]


from agentlab.agents.agent_args import AgentArgs


@dataclass
class DemoTestAgentArgs(AgentArgs):
    agent_name: str = "TestAgent"

    def make_agent(self) -> bgym.Agent:
        return DemoTestAgent()

    def set_reproducibility_mode(self):
        self.temperature = 0

    def prepare(self):
        return self.chat_model_args.prepare_server()

    def close(self):
        return self.chat_model_args.close_server()


@dataclass
class MockChatModelArgs:
    llm_model: str = "None"

    def prepare_server(self):
        return

    def close_server(self):
        return


class DemoTestAgent(bgym.Agent):
    def __init__(self):
        self.chat_model_args = MockChatModelArgs()
        self.action_set = bgym.HighLevelActionSet(["workarena++"], multiaction=False)

    def get_action(self, obs: Any) -> tuple[str, dict]:

        action = "goto('http://localhost:1234')"
        return (
            action,
            bgym.AgentInfo(
                think="thought",
                chat_messages="messages",
                stats={"prompt_length": 0, "response_length": 0},
                extra_info={"chat_model_args": asdict(self.chat_model_args)},
            ),
        )
