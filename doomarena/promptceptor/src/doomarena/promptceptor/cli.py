
import argparse
from pathlib import Path

from doomarena.promptceptor.replay import replay_missing_outputs
from doomarena.promptceptor.integrations import PATCHER_REGISTRY

def build_parser():
    parser = argparse.ArgumentParser(
        description="Replay missing outputs from LLM logs."
    )
    parser.add_argument("log_root", type=Path, help="Path to the root log directory")
    parser.add_argument(
        "--stream",
        type=str,
        choices=["true", "false", "same"],
        default="same",
        help="Whether to stream output: true, false, or same (preserve original)",
    )
    parser.add_argument(
        "--overwrite",
        type=str,
        choices=["always", "never", "if_newer"],
        default="if_newer",
        help="Overwrite mode for recomputation",
    )
    parser.add_argument(
        "--patcher",
        type=str,
        default="same",
        choices=['same'] + list(PATCHER_REGISTRY.keys()),
        help="Which patcher/integration to use (e.g., by default reuses 'same' one)",
    )
    return parser


def main():

    parser = build_parser()
    args = parser.parse_args()

    if not args.log_root.exists():
        parser.error(f"The path {args.log_root} does not exist.")

    # Resolve stream argument
    stream_map = {"true": True, "false": False, "same": None}
    stream = stream_map[args.stream]

    # Instantiate the selected patcher
    if args.patcher != "same":
        patcher_class = PATCHER_REGISTRY[args.patcher]
    else:
        patcher_class = "same"
        
    replay_missing_outputs(
        log_root=args.log_root,
        patcher_class=patcher_class,
        stream=stream,
        overwrite_mode=args.overwrite,
    )