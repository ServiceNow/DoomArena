from doomarena.promptceptor.patch import patch_llm_method
from doomarena.promptceptor.integrations.base import BasePatcher
from pathlib import Path
import types

class Dummy:
    def do_something(self, x):
        return {"result": x * 2}

class DummyPatcher(BasePatcher):
    def extract_content(self, response, is_streaming=False):
        return str(response["result"])

    @classmethod
    def name(cls): return "dummy"

    def patch_client(self): return None
    def call_client(self, *args, **kwargs): return None

def test_patch_llm_method_logs_output(tmp_path):
    dummy = Dummy()
    method_name = "do_something"
    patcher = DummyPatcher(log_dir=tmp_path)

    patch_llm_method(dummy, method_name, patcher)

    result = getattr(dummy, method_name)(5)
    assert result["result"] == 10

    logs = list(tmp_path.rglob("output.txt"))
    assert logs, "Expected an output.txt log file"
    assert logs[0].read_text().strip() == "10"
