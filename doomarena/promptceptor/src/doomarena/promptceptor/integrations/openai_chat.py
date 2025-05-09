from pathlib import Path
from .base import BasePatcher


class OpenAIChatPatcher(BasePatcher):
    @classmethod
    def name(cls) -> str:
        return "openai_chat"

    def patch_client(self) -> Path:
        from ..patch import patch_llm_method
        import openai
        import openai.resources.responses.responses

        output_folder = patch_llm_method(
            target_object=openai.resources.chat.completions.Completions,
            method_name="create",
            patcher=self,
        )
        return output_folder

    def extract_content(self, response, is_streaming=False) -> str:
        import openai
        from openai.types.chat import ChatCompletionChunk

        if is_streaming:
            if isinstance(response, ChatCompletionChunk):
                return response.choices[0].delta.content
            else:
                return ''
        else:
            assert isinstance(
                response, openai.types.chat.chat_completion.ChatCompletion
            )
            return response.choices[0].message.content

    def call_client(self, *args, **kwargs):
        from ..patch import get_unwrapped_method
        import openai
        from openai import OpenAI

        client = OpenAI()

        method = get_unwrapped_method(
            target_object=client.chat.completions,  # we use the instance instead of the class here
            method_name="create",
        )

        response = method(
            *args, **kwargs
        )
        return response