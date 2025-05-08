import pytest
from pathlib import Path
from doomarena.promptceptor.integrations.openai_responses import OpenAIResponsesPatcher
from doomarena.promptceptor.replay import replay_missing_outputs
from openai import OpenAI


@pytest.fixture(scope="module")
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

    _ = client.responses.create(
        model="gpt-4o-mini",
        input="Tell me 3 facts about quantum physics. One line each.",
        stream=True
    )

    return output_folder


@pytest.mark.local
def test_openai_logging(patched_openai_with_logs):
    input_files = list(patched_openai_with_logs.rglob("input.yaml"))
    output_files = list(patched_openai_with_logs.rglob("output.txt"))

    assert input_files, "Expected at least one input.yaml file"
    assert output_files, "Expected at least one output.txt file"


@pytest.mark.local
def test_openai_replay(patched_openai_with_logs):
    for output_file in patched_openai_with_logs.rglob("output.txt"):
        output_file.unlink()

    replay_missing_outputs(
        log_root=patched_openai_with_logs,
        patcher_class=OpenAIResponsesPatcher,
        stream=False,
        overwrite_mode="never",
    )

    restored_outputs = list(patched_openai_with_logs.rglob("output.txt"))
    assert restored_outputs, "Expected output.txt to be regenerated"
