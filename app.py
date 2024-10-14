from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import gptcall
import re

app = Flask(__name__)
CORS(app)

system_message = """\
Given the user query and starting code, return only the code for solving it. \
Only change/add what is required to solve the query. \
Adhere and edit/add directly on the user's code so that there are as least deletions as possible, only where required. \
Do not remove/update code if it's not directly required from the query!!\
"""

def gen_prompt(prompt, code):
    return f"User query: {prompt}\nUser code: {code}"

def extract_code(code):
    code = re.search(r'```(.*?)\n(.*?)```', code, re.DOTALL)
    if code:
        return code.group(2)
    return code

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    model = data.get('model', 'gpt-4o')
    prompt = data.get('prompt', '')
    code = data.get('code', '')

    actual_prompt = gen_prompt(prompt, code)

    combined_result, _, status = gptcall(
        actual_prompt,
        model=model,
        system_message=system_message,
        seed=42
    )
    if status == 'stop':
        output_code = extract_code(combined_result)
        return jsonify({'updatedCode': output_code}), 200
    return jsonify({'error': status}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
