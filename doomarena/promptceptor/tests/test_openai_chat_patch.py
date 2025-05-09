import pytest
from pathlib import Path
from doomarena.promptceptor.integrations.openai_chat import OpenAIChatPatcher
from doomarena.promptceptor.replay import replay_missing_outputs
from openai import OpenAI


@pytest.fixture()
def patched_openai_chat_with_logs(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("openai_chat_logs")
    patcher = OpenAIChatPatcher(log_dir=tmp_path)
    output_folder = patcher.patch_client()

    client = OpenAI()

    # Non-streaming call
    _ = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "Write a one-sentence bedtime story about a unicorn."
        }],
        stream=False
    )

    # Streaming call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "Tell me a bedtime story in 2 short lines."
        }],
        stream=True
    )
    for _ in response:
        pass  # Consume the streamed chunks

    return output_folder


@pytest.mark.local
def test_openai_chat_logging(patched_openai_chat_with_logs):
    input_files = list(patched_openai_chat_with_logs.rglob("input.yaml"))
    output_files = list(patched_openai_chat_with_logs.rglob("output.txt"))

    assert len(input_files) == 2, "Expected at least one input.yaml file"
    assert len(output_files) == 2, "Expected at least one output.txt file"

    for output_file in patched_openai_chat_with_logs.rglob("output.txt"):
        output_file.unlink()

    replay_missing_outputs(
        log_root=patched_openai_chat_with_logs,
        patcher_class=OpenAIChatPatcher,
        stream=None,  # use original stream setting from input.yaml
        overwrite_mode="never",
    )

    restored_outputs = list(patched_openai_chat_with_logs.rglob("output.txt"))
    assert len(restored_outputs) == 2, f"Expected number of output.txt files to be 2, but got {len(restored_outputs)}"
