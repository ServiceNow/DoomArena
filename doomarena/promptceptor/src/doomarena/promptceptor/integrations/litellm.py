from .base import BasePatcher

class LiteLLMPatcher(BasePatcher):
    @classmethod
    def name(cls) -> str:
        return "litellm"

    def patch_client(self):
        from ..patch import patch_llm_method
        import litellm

        return patch_llm_method(
            target_object=litellm,
            method_name="completion",
            patcher=self,
        )

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