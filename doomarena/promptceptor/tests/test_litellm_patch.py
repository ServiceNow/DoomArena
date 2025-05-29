from doomarena.promptceptor.replay import replay_missing_outputs
import pytest
import tempfile
from pathlib import Path
from doomarena.promptceptor.integrations.litellm import LiteLLMPatcher
import litellm


@pytest.fixture()
def patched_litellm_with_logs(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("litellm_logs")
    patcher = LiteLLMPatcher(log_dir=tmp_path)
    output_folder = patcher.patch_client()

    _ = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Summarize the Moon in one sentence."}],
        stream=False,
        temperature=0.3
    )
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Summarize the Sun in one sentence."}],
        stream=True,
        temperature=0.3
    )
    for chunk in response:
        print(f".", end="", flush=True)
    return output_folder


@pytest.mark.local
def test_litellm_patch(patched_litellm_with_logs):
    input_files = list(patched_litellm_with_logs.rglob("input.yaml"))
    output_files = list(patched_litellm_with_logs.rglob("output.txt"))
    assert len(input_files) == 2, "Expected at least one input.yaml file"
    assert len(output_files) == 2, "Expected at least one output.txt file"

    for output_file in patched_litellm_with_logs.rglob("output.txt"):
        output_file.unlink()

    replay_missing_outputs(
        log_root=patched_litellm_with_logs,
        patcher_class=LiteLLMPatcher,
        stream=False,
        overwrite_mode="never",
    )

    restored_outputs = list(patched_litellm_with_logs.rglob("output.txt"))
    assert len(restored_outputs) == 2, f"Expected number of output.txt files to be 2, but got {len(restored_outputs)}"
