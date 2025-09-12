from operator import is_
from .base import BasePatcher
from pathlib import Path
import yaml

class LiteLLMPatcher(BasePatcher):
    @classmethod
    def name(cls) -> str:
        return "litellm"

    def __init__(self, log_dir: Path, text_only: bool = False):
        super().__init__(log_dir=log_dir)
        self.text_only = text_only

    def patch_client(self):
        from ..patch import patch_llm_method
        import litellm

        return patch_llm_method(
            target_object=litellm,
            method_name="completion",
            patcher=self,
        )

    def extract_content(self, response, is_streaming=False) -> str:
        import openai
        from openai.types.chat import ChatCompletionChunk

        if self.text_only:
            if is_streaming:
                # Assumes streamed chunks follow OpenAI's format
                return (
                    response.get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content", "")
                )
            return response["choices"][0]["message"]["content"]

        assert not is_streaming, "Non-text mode does not support streaming"

        response_dict = response.to_dict()
        response_yaml = yaml.safe_dump(response_dict)
        return response_yaml
            
    def call_client(self, *args, **kwargs):
        from ..patch import get_unwrapped_method
        import litellm

        method = get_unwrapped_method(
            litellm, "completion"
        )

        response = method(
            *args, **kwargs
        )
        return response