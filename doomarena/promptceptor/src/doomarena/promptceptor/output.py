
from pathlib import Path

from doomarena.promptceptor.integrations.base import BasePatcher

from pathlib import Path
import yaml


def convert_tuples_to_lists(obj):
    if isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, list):
        return [convert_tuples_to_lists(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_tuples_to_lists(v) for k, v in obj.items()}
    return obj


def dump_yaml_with_block_literals(obj, remove_trailing_whitespace: bool = True):
    """
    Dumps any Python object (typically a dict or list) into a YAML string,
    using block literal (|) style for multi-line strings where appropriate.
    """
    obj = convert_tuples_to_lists(obj)

    def str_presenter(dumper, data):
        if "\n" in data:
            if remove_trailing_whitespace:
                # Remove trailing whitespace from each line
                data = "\n".join(line.rstrip() for line in data.splitlines())
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)

    return yaml.dump(obj, sort_keys=False, allow_unicode=True)


def create_indexed_subfolder(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)

    # Try up to a large max index (can adjust as needed)
    for idx in range(10_000_000):
        candidate = folder / str(idx)
        try:
            # atomic mkdir; only succeeds if folder doesn't exist
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
        except Exception as e:
            raise RuntimeError(f"Failed to create subfolder {candidate}") from e

    raise RuntimeError("Failed to create an indexed subfolder: index space exhausted")


def write_llm_output(
    response,
    output_file: Path,
    patcher: BasePatcher,
    stream: bool,
    show_logs: bool = True,
):
    if stream:
        def streaming_wrapper():
            with open(output_file, "w", encoding="utf-8") as outf:
                for chunk in response:
                    content = patcher.extract_content(chunk, is_streaming=True)
                    if content:
                        outf.write(content)
                        outf.flush()
                    yield chunk
            if show_logs:
                print(f"🟢 Finished streamed-writing to {output_file}")
        return streaming_wrapper()
    else:
        content = patcher.extract_content(response, is_streaming=False)
        with open(output_file, "w", encoding="utf-8") as outf:
            outf.write(content)
        if show_logs:
            print(f"🟢 Finished writing to {output_file}")
        return response