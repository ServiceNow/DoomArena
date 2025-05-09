from math import log
from typing import Literal, Type
from pathlib import Path
from doomarena.promptceptor.integrations import PATCHER_REGISTRY
from doomarena.promptceptor.output import write_llm_output
import yaml
from functools import wraps
from doomarena.promptceptor.integrations.base import BasePatcher


YELLOW = "\033[93m"
RESET = "\033[0m"


def _should_recompute(
    input_path: Path,
    output_file: Path,
    overwrite_mode: Literal["always", "never", "if_newer"],
) -> bool:
    if overwrite_mode == "always":
        return True
    if overwrite_mode == "never":
        return not output_file.exists()
    if overwrite_mode == "if_newer":
        if not output_file.exists():
            return True
        return input_path.stat().st_mtime > output_file.stat().st_mtime
    raise ValueError(f"Unknown overwrite_mode: {overwrite_mode}")


def replay_missing_outputs(
    log_root: Path,
    patcher_class: Type[BasePatcher] | Literal["same"] = "same",
    stream: bool | None = None,
    overwrite_mode: Literal["always", "never", "if_newer"] = "if_newer",
):
    """
    Recursively scans for input.yaml files under `log_root`.
    For any input.yaml missing an output.txt or error.txt, it calls the target_func
    with stored args and kwargs, preserving stream behavior.
    """
    print(f"\n📂 Scanning logs in: {log_root}")

    inputs_to_process = []
    total_inputs = 0

    for path in log_root.rglob("input.yaml"):
        total_inputs += 1
        folder = path.parent
        output_file = folder / "output.txt"
        # error_file = folder / "error.txt"

        if _should_recompute(path, output_file, overwrite_mode):
            inputs_to_process.append(path)

    print(f"🔍 Total input.yaml files found: {total_inputs}")
    print(f"🛠️  Needing recomputation:       {len(inputs_to_process)}\n")

    for i, input_path in enumerate(inputs_to_process):
        folder = input_path.parent
        output_file = folder / "output.txt"
        error_file = folder / "error.txt"

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = yaml.load(f, yaml.FullLoader)

            args = data.get("args", [])
            kwargs = data.get("kwargs", {})

            if stream is not None:
                kwargs["stream"] = stream

            stream = kwargs.get("stream", False)

            print(f"🔄 [{i}/{len(inputs_to_process)}] Replaying: {input_path.relative_to(log_root)}")
            
            if patcher_class != "same":
                patcher: BasePatcher = patcher_class(log_dir=log_root)
            else:
                patcher_name = data["patcher"]
                patcher: BasePatcher = PATCHER_REGISTRY[patcher_name](log_dir=log_root)
                
            response = patcher.call_client(*args, **kwargs)

            output = write_llm_output(
                response=response,
                output_file=output_file,
                patcher=patcher,
                stream=stream,
                show_logs=False,  # quieter in batch mode
            )
            if stream:
                # Iterate over the generator to ensure it finishes
                for chunk in output:
                    print(f".", end="", flush=True)

            print(f"   ✅ Wrote: {output_file.relative_to(log_root)}")

        except Exception as e:
            with open(error_file, "w", encoding="utf-8") as ef:
                ef.write(f"Error during replay:\n{repr(e)}\n")
            print(f"   ❌ Error (logged to {error_file.relative_to(log_root)})")

    print(f"n🏁 Done processing all inputs from {log_root}\n")
