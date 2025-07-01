# server.py
from flask import Flask, render_template, request, jsonify
from new_tester import process  # your processing function

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def api_process():
    data = request.get_json() or {}
    text = data.get('text', '')
    output = process(text)
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
