# Test that doomarena/core/src/doomarena/__init__.py does not exist
from pathlib import Path


def test_no_init_in_namespace():
    init_file = Path(__file__).parent.parent / "src" / "doomarena" / "__init__.py"
    print(f"Checking for __init__.py in {init_file}")
    assert (
        not init_file.exists()
    ), f"{init_file} should not exist for a namespace package. Delete it or this will break imports"


def test_namespace_importable():
    import importlib

    try:
        importlib.import_module("doomarena.core")
        importlib.import_module("doomarena.mailinject")
    except ModuleNotFoundError as e:
        raise AssertionError(f"Namespace package broken: {e}")
