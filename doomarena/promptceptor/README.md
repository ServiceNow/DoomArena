# Promptceptor

DoomArena Promptceptor (prompt interceptor) is a minimalistic tool for 
prompt engineering, red-teaming and debugging of AI agents.


## Overview

Promptceptor works by monkey-patching common LLM API clients such as OpenAI and LiteLLM to track and store the prompt, parameters and completion of every LLM call in a simple folder structure on the disk.
Streaming mode is supported.

The calls can then be modified and replayed for quick prototyping of prompt injection attacks and prompt-based defenses, with the option of changing the model and sampling parameters.

## Supported clients

- OpenAI Chat Completions API: non-streaming and streaming.
- OpenAI Responses API: non-streaming and streaming  # Function calls may not be supported yet
- LiteLLM: non-streaming and streaming

## Quick start

1. Install this package
```bash
pip install doomarena-promptceptor
```

Or install it locally for development
```bash
pip install -e doomarena/promptceptor
pytest doomarena/promptceptor  # run the tests (may require some API keys)
```

2. Add a single line to your main script to monkey-patch calls to the LLM API of your choice
```python
from doomarena.promptceptor.integrations.openai_chat import OpenAIChatPatcher

# Add this in main thread / initialization / setup function
output_folder = OpenAIChatPatcher(log_dir='logs').patch_client() 

# All subsequent calls will be logged to output_folder
client = OpenAI()
print("\n▶ Running non-streaming chat completion...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Write a one-sentence bedtime story about a unicorn."
        }
    ],
    stream=False
)
```

Check out the examples in `./src/doomarena/promptceptor/examples` for more info on supported LLM API Clients.


3. Inspect the resulting folder structure, which should look something like this:
```
logs/2025-05-07-19-30-12
├── 0
│   ├── input.yaml
│   └── output.txt
└── 1
│   ├── input.yaml
│   └── output.txt
├── 2
│   ├── input.yaml
│   └── output.txt
...
```

Each call to the LLM API will result in a new subfolder (e.g. `0`, `1`, `2`) containing
the input call to the LLM `input.yaml` and the raw output `output.txt`.
Multithreading and multiprocessing is supported but may result in gaps in the indices or several subfolders (not a big deal).

4. Modify and recompute.

If you're curious how a different input may have affected you can modify the prompt messages inside `input.yaml`,
as well as the model (e.g. switch from `gpt-4o` to `claude`), temperature, and any other `**kwargs` exposed by the LLM API client.

Then, recompute the outputs with
```bash
promptceptor path/to/logs
```

Promptceptor will recompute the output if `output.txt` is missing or the `input.yaml` timestamp is newer (see `--overwrite` parameter for more details).


## Examples

You can run and inspect examples of patching OpenAI and LiteLLM clients
```bash
# Export relevant API keys here
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...

python -m doomarena.promptceptor.scripts.litellm_example
python -m doomarena.promptceptor.scripts.openai_example
```
