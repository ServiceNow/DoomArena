import os
from pathlib import Path
from tapeagents.llms import LiteLLM


# Make the cache dir if not exists
cache_dir = Path(".cache")
cache_dir.mkdir(exist_ok=True)

TOKENIZER_NAME = "microsoft/Phi-3-medium-128k-instruct"  # just use any model with chat template / only for token counting purposes

Phi3 = LiteLLM(
    model_name="openrouter/microsoft/Phi-3-medium-128k-instruct",
    stream=False,
    tokenizer_name=TOKENIZER_NAME,
    parameters=dict(temperature=0, max_tokens=2048),
    use_cache=True,
)
GPT4o = LiteLLM(
    model_name="openrouter/openai/gpt-4o-mini",
    stream=False,
    tokenizer_name=TOKENIZER_NAME,
    parameters=dict(temperature=0, max_tokens=2048),
    use_cache=True,
)
Llama3 = LiteLLM(
    model_name="openrouter/meta-llama/llama-3.3-70b-instruct",
    stream=False,
    tokenizer_name=TOKENIZER_NAME,
    parameters=dict(temperature=0, max_tokens=2048),
    use_cache=True,
)


# MODEL_NAME = "openrouter/meta-llama/llama-3.3-70b-instruct"
MODEL_NAME = os.getenv("MAILINJECT_MODEL_NAME", "openrouter/openai/gpt-4o-2024-11-20")
# MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
TOKENIZER_NAME = "microsoft/Phi-3-medium-128k-instruct"  # just use any model with chat template / only for token counting purposes

MODEL_FOR_TESTING = LiteLLM(
    model_name=MODEL_NAME,
    stream=False,
    tokenizer_name=TOKENIZER_NAME,
    parameters=dict(temperature=0, max_tokens=2048),
    use_cache=True,
)
