from pathlib import Path
import os
import threading
import datetime
from pathlib import Path
from functools import wraps

from .integrations.base import BasePatcher
from .output import create_indexed_subfolder, dump_yaml_with_block_literals, write_llm_output


YELLOW = "\033[93m"
RESET = "\033[0m"


def patch_llm_method(
    target_object,
    method_name: str,
    patcher: BasePatcher,
) -> Path:
    """
    Monkey-patch a method (e.g., litellm.completion)
    to log inputs/outputs thread- and process-safely.

    See examples for provider-specific usage.

    Args:
        target_object: The object or module (e.g., openai.ChatCompletion).
        method_name (str): The name of the method to patch (e.g., "create").
        log_dir (Path): Base path to store logs.
    """
    attr = getattr(target_object, method_name)
    if getattr(attr, "_is_patched_promptceptor", False):
        return  # Already patched; skip
    target_object._is_patched_promptceptor = True

    name = getattr(target_object, '__name__', type(target_object).__name__)
    print(f"{YELLOW}LLMInspector: Patching {name}.{method_name}{RESET}")


    original_method = attr

    # Create a session folder with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    folder = patcher.log_dir / f"{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)

    print(f"{YELLOW}LLMInspector: Logging to {folder}{RESET}")

    @wraps(original_method)
    def wrapper(*args, **kwargs):
        stream = kwargs.get("stream", False)

        pid = os.getpid()
        tid = threading.get_ident()

        subfolder = create_indexed_subfolder(folder)

        input_file = subfolder / "input.yaml"
        output_file = subfolder / "output.txt"

        # Log all args and kwargs so they can be dumped to YAML and later read back
        all_inputs = {
            "patcher": patcher.name(),
            "args": [],  # drop the args for now due to issues with OpenAI Responses
            "kwargs": kwargs,
        }

        with open(input_file, "w", encoding="utf-8") as f:
            f.write(dump_yaml_with_block_literals(all_inputs))

        print(f"{YELLOW}Intercepted LLM call -> logging to {input_file}{RESET}")

        try:
            response = original_method(*args, **kwargs)
        except Exception as e:
            with open(subfolder / "error.txt", "w", encoding="utf-8") as f:
                f.write(str(e))
            raise

        return write_llm_output(
            response,
            output_file,
            patcher,
            stream,
            show_logs=True,
        )

    setattr(target_object, method_name, wrapper)

    return folder
