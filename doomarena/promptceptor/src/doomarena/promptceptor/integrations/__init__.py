from .litellm import LiteLLMPatcher
from .openai_responses import OpenAIResponsesPatcher

PATCHER_REGISTRY = {
    LiteLLMPatcher.name(): LiteLLMPatcher,
    OpenAIResponsesPatcher.name(): OpenAIResponsesPatcher,
}