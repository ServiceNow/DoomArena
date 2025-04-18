from doomarena.core.agent_defenses.base import SafetyCheck
from litellm import completion
from openai import OpenAIError
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import TYPE_CHECKING, Any, Union
from langchain.schema import BaseMessage
from doomarena.core.agent_defenses.llamaguard_api import LlamaGuardSafetyCheckAPI


# Add these functions before the FewShotToolCallingAgent class
def retry_if_rate_limit_error(exception):
    return isinstance(exception, OpenAIError) and "token rate limit" in str(exception)


@retry(
    wait=wait_random_exponential(min=1, max=30),
    stop=stop_after_attempt(10),
    retry=retry_if_rate_limit_error,
)
def generate_with_backoff(**kwargs):
    return completion(**kwargs)


# Define the SafeCompletionWrapper class
class SafeCompletionWrapper:
    def __init__(self, safety_check: SafetyCheck, abort):
        self.safety_check = safety_check
        self.abort = abort

    def safe_completion(
        self,
        messages=None,
        model=None,
        custom_llm_provider=None,
        tools=None,
        temperature=None,
    ):
        # Pass the messages through the safety check
        res = self.safety_check.check(messages=messages)
        if len(res) != 0:
            if self.abort:
                raise Exception("Aborting")
            else:
                messages[-1]["content"] += (
                    "This action is unsafe because of the following categories: ".join(
                        res
                    )
                    + "Please take any future actions with caution."
                )
        # Call the original completion function
        return generate_with_backoff(
            messages=messages,
            model=model,
            custom_llm_provider=custom_llm_provider,
            tools=tools,
            temperature=temperature,
        )


safety_check = LlamaGuardSafetyCheckAPI


def safe_init(self, messages: Union[list[BaseMessage], BaseMessage] = None):
    print("safe discussion called")
    if isinstance(messages, BaseMessage):
        messages = [messages]
    elif messages is None:
        messages = []

    res = LlamaGuardSafetyCheckAPI.check_bgym(messages)
    abort = 1
    if len(res) != 0:
        if abort:
            raise Exception("Aborting")
        else:
            messages[0]["content"] += (
                "This request is unsafe because of the following categories: ".join(res)
                + "Please take any future actions with caution."
            )
    self.messages = messages
