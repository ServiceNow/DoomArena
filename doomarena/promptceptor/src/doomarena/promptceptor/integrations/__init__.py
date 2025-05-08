from .litellm import LiteLLMPatcher
from .openai_responses import OpenAIResponsesPatcher
from .openai_chat import OpenAIChatPatcher

PATCHER_REGISTRY = {
    LiteLLMPatcher.name(): LiteLLMPatcher,
    OpenAIResponsesPatcher.name(): OpenAIResponsesPatcher,
    OpenAIChatPatcher.name(): OpenAIChatPatcher,
}