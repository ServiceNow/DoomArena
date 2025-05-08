# Promptceptor

DoomArena Promptceptor (prompt interceptor) is a minimalistic tool for 
prompt engineering, red-teaming and debugging of AI agents.


## Overview

Promptceptor works by monkey-patching common LLM API clients such as OpenAI and LiteLLM to track and store the prompt, parameters and completion of every LLM call in a simple folder structure on the disk.
Streaming mode is supported.

The calls can then be modified and replayed for quick prototyping of prompt injection attacks and prompt-based defenses, with the option of changing the model and sampling parameters.


## Quick start

1. Install this package
```bash
pip install doomarena-promptceptor
```

Or install it locally for development
```bash
pip install doomarena/prompceptor
```

2. Add a single line to your main script (preferably in the main thread) to monkey
```python
from doomarena.promptceptor import patch_llm_method

# add this in main thread / initialization / setup function
patch_llm_method(litellm, "completion")  
```


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
