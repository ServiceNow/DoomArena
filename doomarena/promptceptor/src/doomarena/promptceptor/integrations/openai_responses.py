from pathlib import Path
from .base import BasePatcher


class OpenAIResponsesPatcher(BasePatcher):
    @classmethod
    def name(cls) -> str:
        return "openai_responses"
    
    def patch_client(self) -> Path:
        from ..patch import patch_llm_method
        import openai

        output_folder = patch_llm_method(
            target_object=openai.resources.responses.responses.Responses,
            method_name="create",
            patcher=self,
        )
        return output_folder

    def extract_content(self, response, is_streaming=False) -> str:
        import openai
        from openai.types.responses import ResponseTextDeltaEvent

        if is_streaming:
            if isinstance(response, ResponseTextDeltaEvent):
                # If the response is a delta event, return the delta text
                return response.delta
            else:
                return ''
        else:
            assert isinstance(
                response, openai.resources.responses.responses.Response
            )
            return response.output_text  # response.output[0].content[0].text
        
    def call_client(self, *args, **kwargs):
        from openai import OpenAI

        client = OpenAI()
        response = client.responses.create(
            *args, **kwargs
        )
        return response