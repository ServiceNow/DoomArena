import pytest
from doomarena.taubench.scripts.attack_script import (
    main as run_tau_bench_attack_main,
)
from pathlib import Path

CONFIG_FILE_PATH = (
    Path(__file__).resolve().parent / "test_data" / "malicious_user_attack.yaml"
)


@pytest.mark.local
def test_run_tau_bench_attack():
    """Constructs an argparse.Namespace and calls run() directly to ensure it executes without errors."""
    try:
        results = run_tau_bench_attack_main(
            [
                "--config",
                str(CONFIG_FILE_PATH),
            ]
        )
        assert isinstance(results, list), "Run did not return a list"
    except Exception as e:
        pytest.fail(f"run_tau_bench_attack:run() raised an unexpected exception: {e}")
