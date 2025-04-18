from dataclasses import dataclass
from agentlab.agents import dynamic_prompting as dp
from agentlab.llm.llm_utils import HumanMessage, parse_html_tags_raise
from typing import List
from doomarena.core.attacks.attacks import Attacks
from doomarena.core.success_filters import SuccessFilter
import ast, json


@dataclass
class RedTeamPromptFlags(dp.Flags):
    """Extended flags for red teaming agent"""

    obs: dp.ObsFlags
    enable_chat: bool = False
    max_prompt_tokens: int = None
    extra_instructions: str | None = None
    max_trunc_itr: int = 20
    success_filters: List[SuccessFilter] = None  # The objectives of the attacks
    attacks: List[Attacks] = None  # The list of attacks


class RedTeamPrompt(dp.Shrinkable):
    def __init__(
        self,
        obs_history: list[dict],
        flags: RedTeamPromptFlags,
    ) -> None:
        super().__init__()
        self.flags = flags

        # Get instructions directly from generator
        self.instructions = (
            "Here is a description of past observatins and actions taken by the agent."
        )
        self.obs = dp.Observation(
            obs_history[-1],
            self.flags.obs,
        )

    @property
    def _prompt(self) -> HumanMessage:
        prompt = HumanMessage(self.instructions)
        prompt.add_text(
            f"""\
{self.obs.prompt}\
"""
        )
        attack_descriptions = "\n".join(
            [attack.description for attack in self.flags.attacks]
        )
        prompt.add_text(attack_descriptions)
        prompt.add_text(
            """
Make sure to follow the instructions carefully and return the result in the appropriate format.
"""
        )

        return self.obs.add_screenshot(prompt)

    def _parse_answer(self, text_answer):
        ans_dict = {}
        chain_of_thought = parse_html_tags_raise(text_answer, optional_keys=["think"])
        ans_dict.update(chain_of_thought)
        tags = [attack.answer_tag for attack in self.flags.attacks]
        additional_content = parse_html_tags_raise(
            text_answer,
            optional_keys=tags,
        )
        if additional_content:
            # Parse string representations of dictionaries into actual dictionaries
            for key, value in additional_content.items():
                try:
                    # First try using ast.literal_eval which can handle Python dict syntax
                    parsed_value = ast.literal_eval(value)
                    additional_content[key] = parsed_value
                except (ValueError, SyntaxError):
                    # If that fails, try cleaning up the string and parsing as JSON
                    try:
                        # Replace Python-style quotes with JSON-style quotes
                        json_str = value.replace("'", '"')
                        parsed_value = json.loads(json_str)
                        additional_content[key] = parsed_value
                    except json.JSONDecodeError:
                        # If both parsing attempts fail, keep the original string
                        continue

            ans_dict.update(additional_content)
        return ans_dict

    def shrink(self):
        super().shrink()
