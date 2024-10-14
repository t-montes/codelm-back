from flask import Flask, request, jsonify
from service import Service
from flask_cors import CORS

app = Flask(__name__)
s = Service(
    seed = 42,
    default_model = 'gpt-4o',
    tokenize_level = 'word',
    python_print=True
)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    response = s.process(**data)
    return jsonify(response), (400 if 'error' in response else 200)

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
