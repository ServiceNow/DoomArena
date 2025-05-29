from pathlib import Path
from .base import BasePatcher


class OpenAIResponsesPatcher(BasePatcher):
    @classmethod
    def name(cls) -> str:
        return "openai_responses"
    
    def patch_client(self) -> Path:
        from ..patch import patch_llm_method
        import openai
        import openai.resources.responses.responses

        output_folder = patch_llm_method(
            target_object=openai.resources.responses.responses.Responses,
            method_name="create",
            patcher=self,
        )
        return output_folder

    def extract_content(self, response, is_streaming=False) -> str:
        import openai
        from openai.types.responses import ResponseTextDeltaEvent, Response

        if is_streaming:
            if isinstance(response, ResponseTextDeltaEvent):
                # If the response is a delta event, return the delta text
                return response.delta
            else:
                return ''
        else:
            assert isinstance(
                response, Response
            )
            return response.output_text  # response.output[0].content[0].text
        
    def call_client(self, *args, **kwargs):
        from ..patch import get_unwrapped_method
        import openai
        from openai import OpenAI
        client = OpenAI()

        method = get_unwrapped_method(
            target_object=client.responses,
            method_name="create",
        )

        response = method(
            *args, **kwargs
        )
        return response