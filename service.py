from utils import gptcall, serpcall, diff
from transformers import AutoTokenizer
from typing import Callable
import re

system_message = """\
Given the user query and starting code, return only the code for solving it. \
Only change/add what is required to solve the query. \
Adhere and edit/add directly on the user's code so that there are as least deletions as possible, only where required. \
Do not remove/update code if it's not directly required from the query!!\
"""

def gen_prompt(prompt, code):
    if prompt and code:
        return f"User query: {prompt}\nUser code: {code}"
    elif prompt:
        return f"User query: {prompt}. Please provide the code to solve it."
    elif code:
        return f"User query: Solve the requirements stated in the code\nUser code: {code}"

def extract_code(code):
    code = re.search(r'```(.*?)\n(.*?)```', code, re.DOTALL)
    if code:
        return code.group(2)
    return code

class Service:
    encode: Callable[[str], list]
    decode: Callable[[list], str]

    def __init__(self, seed=None, default_model='gpt-4o', tokenize_level='code'):
        self.seed = seed # seed for deterministic completions, if set
        self.default_model = default_model # default completion model to use
        match tokenize_level:
            case 'code':
                tokenizer = AutoTokenizer.from_pretrained("gpt2")
                self.encode = lambda x: tokenizer.encode(x, add_special_tokens=False)
                self.decode = lambda x: tokenizer.decode(x)
            case 'line':
                self.encode = lambda x: x.splitlines()
                self.decode = lambda x: '\n'.join(x)
            case 'word':
                self.encode = lambda x: re.findall(r'\w+|[^\w\s]|\s+|\n|\r', x)
                self.decode = lambda x: ''.join(x)
            case _:
                self.encode = lambda x: list(x)
                self.decode = lambda x: ''.join(x)
    
    def process(self, prompt=None, code=None, model=None) -> dict:
        actual_prompt = gen_prompt(prompt, code)
        try:
            combined_result = gptcall(
                actual_prompt,
                model=model if model else self.default_model,
                system_message=system_message,
                seed=self.seed
            )
            output_code = extract_code(combined_result)
            changes = diff(code, output_code, self.encode, self.decode)
            return {'updatedCode': output_code, 'diff': changes}
        except Exception as e:
            return {'error': f"{e}"}
