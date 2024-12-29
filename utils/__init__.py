from re import DOTALL, search

def gen_prompt(prompt, code, gt_docs):
    if not prompt:
        prompt = "Solve the requirements stated in the code."
    if code: code = f"\nUser code:\n```python\n{code}\n```"
    else: code = " Please provide the code to solve it."
    if gt_docs: gt_docs = f"\nGround-truth documents:\n{gt_docs}"
    else: gt_docs = ""
    
    return f"{prompt}{code}{gt_docs}"

def extract_code(code):
    code = search(r'```(.*?)\n(.*?)```', code, DOTALL)
    if code:
        return code.group(2)
    return code

from .gptcall import request as gptcall
from .tgtcall import request as tgtcall
from .serpcall import request as serpcall

from .llm import llmcall
from .diff import diff, reconstruct, show_diff
from .wag import generate_gt_docs_wag