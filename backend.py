import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from agents import run_research
from langchain_core.messages import HumanMessage, AIMessage

groq_api_key = os.environ.get('GROQ_API_KEY')
tavily_api_key = os.environ.get('TAVILY_API_KEY')

if not groq_api_key or not tavily_api_key:
    raise RuntimeError(
        'Missing GROQ_API_KEY or TAVILY_API_KEY environment variables. '
        'Set them in a .env file or the deployment environment.'
    )

app = Flask(__name__)
CORS(app)

@app.route('/api/research', methods=['POST'])
def research():
    payload = request.get_json(force=True)
    query = payload.get('query', '')
    thread_id = payload.get('thread_id', 'session_001')
    history = payload.get('history', [])

    messages = []
    for item in history:
        role = item.get('role')
        if role == 'user':
            messages.append(HumanMessage(content=item.get('text', '')))
        elif role == 'assistant':
            messages.append(AIMessage(content=item.get('text', '')))

    result = run_research(
        query=query,
        conversation_history=messages,
        thread_id=thread_id,
    )
    return jsonify(result)

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'message': 'Agent backend is alive.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
