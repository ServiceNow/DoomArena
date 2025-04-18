from typing import List, Dict, Any
from doomarena.core.agent_defenses.base import SafetyCheck
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from doomarena.core.agent_defenses.llamaguard_utils import *

model_id = "meta-llama/Llama-Guard-3-8B"
device = "cuda"
dtype = torch.bfloat16
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, torch_dtype=dtype, device_map=device
)


def LlamaGuard(chat):
    input_ids = tokenizer.apply_chat_template(chat, return_tensors="pt").to(device)
    output = model.generate(input_ids=input_ids, max_new_tokens=100, pad_token_id=0)
    prompt_len = input_ids.shape[-1]
    res = tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
    res = postprocess(res)
    return res


class LlamaGuardSafetyCheck(SafetyCheck):
    @staticmethod
    def check(messages: List[Dict[str, Any]]) -> str:
        messages = format_chat(messages)
        return LlamaGuard(messages)

    def check_bgym(messages):
        messages = format_chat_bgym(messages)
        return LlamaGuard(messages)
