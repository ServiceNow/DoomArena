from openai import OpenAI
import openai
import requests
import os
from typing import Optional, Sequence
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses import asdict, dataclass
from typing import List, Dict, Any
from doomarena.core.agent_defenses.base import SafetyCheck
from doomarena.core.agent_defenses.llamaguard_utils import *

# Initialize API key from environment variable
api_key = None
env_var_name = "groq_api_key"
if env_var_name in os.environ:
    api_key = os.environ[env_var_name]  # Set API key from environment variable
else:
    api_key = None  # Default to None if not found


@dataclass
class ChatMessage:
    """
    Represents a chat message with a role and optional content.

    Attributes:
        role (str): The role of the message sender (e.g., "user" or "assistant").
        content (Optional[str]): The content of the message. Defaults to None.
    """

    role: str
    content: Optional[str] = None


class LLamaGuard:
    """
    Represents a Groq Llama Guard for content moderation.

    Attributes:
        _client (OpenAI): The OpenAI client for API interactions.
        model (str): The model to use for content moderation.
    """

    def reinit(self, custom_headers):
        self._client = OpenAI(
            base_url=base_url, api_key=api_key, custom_headers=custom_headers
        )

    def __init__(
        self,
        model="llama-guard-3-8b",
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    ) -> None:
        """
        Initializes the Groq Llama Guard with a model and base URL.

        Args:
            model (str): The model to use for content moderation. Defaults to "llama-guard-3-8b".
            base_url (str): The base URL for the Groq API. Defaults to "https://api.groq.com/openai/v1".
        """
        self._client = OpenAI(
            base_url=base_url, api_key=api_key
        )  # Initialize OpenAI client

        self.model = model  # Set the model for content moderation

    def run(self, mm, output=None, cache=None):
        try:
            if cache is None:
                custom_headers = None
            elif cache == False:
                custom_headers = {"x-use-cache": "false"}
            elif cache == True:
                custom_headers = {"x-use-cache": "true"}

            while True:
                try:
                    kwargs = {
                        "messages": mm,
                        "model": self.model,
                        "max_tokens": 512,
                    }
                    if custom_headers:
                        kwargs["extra_headers"] = custom_headers

                    response = self._client.chat.completions.create(**kwargs)

                    break
                except openai.APIStatusError as e:
                    # Check if the status code is 503
                    print("AA", e, e.status_code)
                    if e.status_code == 503:
                        print("Service Unavailable (503)")

                        custom_headers["x-wait-for-model"] = "true"

                    else:
                        print(f"An error occurred: {e.status_code} - {e}")
                        return []
                except openai.OpenAIError as e:
                    # Catch-all for any other OpenAI-related exceptions
                    print(f"An OpenAI error occurred: {e}")
                    return []

            msg = response.choices[0].message.content  # Get the response content

            ret = postprocess(msg)
            return ret

        except Exception as err:
            import traceback

            traceback.print_exc()
            # Handle exceptions by printing the traceback for debugging
            return []  # Return empty list on error


base_url = "https://api.groq.com/openai/v1"

model = LLamaGuard(
    base_url=base_url, api_key=api_key
)  # Create an instance of GroqLLamaGuard


def LlamaGuardAPI(chat):
    print("LlamaGuard called")
    output = model.run(chat)
    return output


class LlamaGuardSafetyCheckAPI(SafetyCheck):
    @staticmethod
    def check(messages: List[Dict[str, Any]]) -> str:
        messages = format_chat(messages)
        return LlamaGuardAPI(messages)

    def check_bgym(messages):
        # processed_messages = format_chat_bgym(messages)

        messages_to_evaluate = []
        for message in messages:
            if message["role"] == "system":
                continue

            content = message["content"]
            if isinstance(message["content"], list):
                # Concatenate
                content = "\n".join(
                    [d["text"] for d in message["content"] if d["type"] == "text"]
                )

            # Merge with previous content if roles are the same
            if (
                messages_to_evaluate
                and messages_to_evaluate[-1].role == message["role"]
            ):
                messages_to_evaluate[-1].content += "\n" + content
            else:  # Just append
                messages_to_evaluate.append(
                    {"role": message["role"], "content": content}
                )

        return LlamaGuardAPI(messages_to_evaluate)
