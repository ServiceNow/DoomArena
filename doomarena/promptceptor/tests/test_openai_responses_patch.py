import pytest
from pathlib import Path
from doomarena.promptceptor.integrations.openai_responses import OpenAIResponsesPatcher
from doomarena.promptceptor.replay import replay_missing_outputs
from openai import OpenAI


@pytest.fixture()
def patched_openai_with_logs(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("openai_logs")
    patcher = OpenAIResponsesPatcher(log_dir=tmp_path)
    output_folder = patcher.patch_client()

    client = OpenAI()
    _ = client.responses.create(
        model="gpt-4o-mini",
        input="Tell me 2 facts about quantum physics. One line each.",
        stream=False
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input="Tell me 3 facts about quantum physics. One line each.",
        stream=True
    )
    for chunk in response:
        print(f".", end="", flush=True)

    return output_folder


@pytest.mark.local
def test_openai_responses(patched_openai_with_logs):
    input_files = list(patched_openai_with_logs.rglob("input.yaml"))
    output_files = list(patched_openai_with_logs.rglob("output.txt"))

    assert len(input_files) == 2, "Expected at least one input.yaml file"
    assert len(output_files) == 2, "Expected at least one output.txt file"

    for output_file in patched_openai_with_logs.rglob("output.txt"):
        output_file.unlink()

    replay_missing_outputs(
        log_root=patched_openai_with_logs,
        patcher_class=OpenAIResponsesPatcher,
        stream=False,
        overwrite_mode="never",
    )

    restored_outputs = list(patched_openai_with_logs.rglob("output.txt"))
    assert len(restored_outputs) == 2, f"Expected number of output.txt files to be 2, but got {len(restored_outputs)}"
