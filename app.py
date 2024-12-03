from flask import Flask, request, jsonify
from service import Service
from flask_cors import CORS

from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
serpapi_key = os.getenv('SERPAPI_KEY')

app = Flask(__name__)
s = Service(seed = 42, default_model = 'gpt-4o', tokenize_level = 'word', openai_api_key=openai_api_key, serpapi_key=serpapi_key)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    try:
        keys = request.headers['Authorization'].replace('Bearer ', '').split(';')
        if len(keys) == 2:
            openai_api_key, serpapi_key = keys
        else:
            openai_api_key, serpapi_key = keys[0], None 
    except:
        openai_api_key, serpapi_key = None, None
    response = s.process(openai_api_key=openai_api_key, serpapi_key=serpapi_key, **data)
    return jsonify(response), (400 if 'error' in response else 200)

@app.route('/ok', methods=['GET'])
def ok():
    return "ok"

@app.route('/test', methods=['POST'])
def test():
    print(request.get_json())
    return { "updatedCode": "def hw():\n    print('Hello, World!')" }

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
