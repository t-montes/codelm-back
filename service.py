from utils import gptcall, tgtcall, serpcall, diff
from typing import Callable
import json
import re

system_message = """\
Given the user query and starting code, return only the code for solving it. \
Only change/add what is required to solve the query. \
Adhere and edit/add directly on the user's code so that there are as least deletions as possible, only where required. \
Do not remove/update code (nor documentation) if it's not directly required from the query! \
For example, if the user query is a function definition, keep the function name and parameters as is, and only update the function body, unless stated. \
The user may or may not provide ground-truth documents useful for solving the query. If they are provided, use them properly. \
"""

def gen_prompt(prompt, code, gt_docs):
    if not prompt:
        prompt = "Solve the requirements stated in the code"
    if code: code = f"\nUser code:\n```python\n{code}\n```"
    else: code = ". Please provide the code to solve it."
    if gt_docs: gt_docs = f"\nGround-truth documents:\n{gt_docs}"
    else: gt_docs = ""
    
    return f"{prompt}{code}{gt_docs}"

def extract_code(code):
    code = re.search(r'```(.*?)\n(.*?)```', code, re.DOTALL)
    if code:
        return code.group(2)
    return code

class Service:
    encode: Callable[[str], list]
    decode: Callable[[list], str]

    def __init__(
            self, 
            seed=None, 
            default_model='gpt-4o', 
            tokenize_level='word', 
            get_usage=False, 
            get_diff=True, 
            openai_api_key=None,
            together_api_key=None,
            serpapi_key=None
        ):
        self.seed = seed # seed for deterministic completions, if set
        self.default_model = default_model # default completion model to use
        self.get_usage = get_usage
        self.get_diff = get_diff
        self.openai_api_key = openai_api_key
        self.together_api_key = together_api_key
        self.serpapi_key = serpapi_key
        match tokenize_level:
            case 'code':
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoder")
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
    
    def process(self, 
                prompt=None, 
                code=None, 
                gt_docs=None, 
                model=None, 
                openai_api_key=None, 
                together_api_key=None,
                serpapi_key=None,
            ) -> dict:
        openai_api_key = openai_api_key if openai_api_key else self.openai_api_key
        together_api_key = together_api_key if together_api_key else self.together_api_key
        serpapi_key = serpapi_key if serpapi_key else self.serpapi_key
        actual_prompt = gen_prompt(prompt, code, gt_docs)
        try:
            result = {}
            combined_result = call(
                actual_prompt,
                model=model if model else self.default_model,
                system_message=system_message,
                seed=self.seed,
                track_usage=self.get_usage,
                api_key=openai_api_key
            )
            if self.get_usage: result_code, result['usage'] = combined_result
            else: result_code = combined_result

            output_code = extract_code(result_code)
            result['updatedCode'] = output_code
            if self.get_diff and code:
                changes = diff(code, output_code, self.encode, self.decode)
                result['diff'] = changes

            return result
        except Exception as e:
            if "Incorrect API key" in f"{e}":
                return {'error': "Incorrect API key"}
            return {'error': f"{e}"}

def call(prompt, model='gpt-4o', **kwargs):
    if model in ['gpt-4o', 'gpt-4o-mini']:
        return gptcall(prompt, model=model, **kwargs)
    elif '/' in model:
        return tgtcall(prompt, model=model, **kwargs)
    else:
        raise NotImplementedError("Platform not supported")
