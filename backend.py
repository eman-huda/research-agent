import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from agents import run_research
from langchain_core.messages import HumanMessage, AIMessage

GROQ_API_KEY = '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'
TAVILY_API_KEY = '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'

os.environ.setdefault('GROQ_API_KEY', GROQ_API_KEY)
os.environ.setdefault('TAVILY_API_KEY', TAVILY_API_KEY)

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
