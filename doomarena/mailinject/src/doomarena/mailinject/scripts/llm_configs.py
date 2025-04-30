from tapeagents.llms import LiteLLM


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