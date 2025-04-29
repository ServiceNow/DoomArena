# MailInject experiments

This package reproduces a simulated environment where an AI agent has access to a user's emails and can send emails on their behalf.
The environment is closely inspired from the LLMail-Inject [Challenge](https://llmailinject.azurewebsites.net/).

The agent is based on the [TapeAgents](https://github.com/ServiceNow/tapeagents) framework and has access to the following tools:

## Setup

```bash
pip install -e .
```

We use LiteLLM client. The provider is specified as the model name (e.g. `openrouter/meta-llama/llama-3.3-70b-instruct`).
Export the relevant API keys in your `.env` (for vscode) and/or .zshrc depending on your provider.
```
export OPENAI_API_KEY="..."  # if using openrouter as a provider
export OPENROUTER_API_KEY="..."  # if using openai as a provider
```

Run tests
```bash
export MAILINJECT_MODEL_NAME="openrouter/openai/gpt-4o-2024-11-20"  # set the model you want to use for the tests
pytest doomarena/mailinject
```