from flask import Flask, request, jsonify
from service import process as c_process
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    response = c_process(**data)
    return jsonify(response), (400 if 'error' in response else 200)

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
