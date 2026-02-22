from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Claw ERP API'})

@app.route('/api/products')
def products():
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
