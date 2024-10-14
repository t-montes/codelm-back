from utils import gptcall, serpcall, diff, reconstruct, show_diff
from flask import jsonify
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

def process(prompt=None, code=None, model='gpt-4o'):
    actual_prompt = gen_prompt(prompt, code)

    try:
        combined_result = gptcall(
            actual_prompt,
            model=model,
            system_message=system_message,
            seed=42
        )
        output_code = extract_code(combined_result)
        changes = diff(code, output_code)
        return {'updatedCode': output_code, 'diff': changes}
    except Exception as e:
        return {'error': f"{e}"}
