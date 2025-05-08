from pathlib import Path
from .base import BasePatcher


class OpenAIChatPatcher(BasePatcher):
    @classmethod
    def name(cls) -> str:
        return "openai_chat"

    def patch_client(self) -> Path:
        from ..patch import patch_llm_method
        import openai

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
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            *args, **kwargs
        )
        return response
