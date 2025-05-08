from abc import ABC, abstractmethod
from pathlib import Path


class BasePatcher(ABC):
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Name of the patcher (e.g., "openai", "litellm")"""
        pass

    @abstractmethod
    def patch_client(self):
        """Patch the LLM client's method (e.g., `create` or `complete`)"""
        pass

    def extract_content(self, response, is_streaming=False) -> str:
        """
        Extracts text content from LLM responses.
        """
        if is_streaming:
            # Assumes streamed chunks follow OpenAI's format
            return (
                response.get("choices", [{}])[0]
                .get("delta", {})
                .get("content", "")
            )
        return response["choices"][0]["message"]["content"]

    @abstractmethod
    def call_client(self):
        """Call the patched client"""
        pass