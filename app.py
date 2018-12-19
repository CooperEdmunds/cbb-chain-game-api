from flask import Flask, jsonify

app = Flask(__name__)

data = {
    'greeting' : 'hey'
}

@app.route('/testroute', methods=['GET'])
def get_tasks():
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run(debug=True)
