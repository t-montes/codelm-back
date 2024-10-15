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
        openai_api_key, serpapi_key = request.headers['Authorization'].replace('Bearer ', '').split(';')
    except:
        openai_api_key, serpapi_key = None, None
    response = s.process(openai_api_key=openai_api_key, serpapi_key=serpapi_key, **data)
    return jsonify(response), (400 if 'error' in response else 200)

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
