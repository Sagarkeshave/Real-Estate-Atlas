from flask import Flask, render_template, request, jsonify
from rag import get_response
# from graph_rag import get_response_with_langgraph_memory
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('message')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    response, _ = get_response(query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5051, debug=True)
