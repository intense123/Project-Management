from flask import Blueprint, request, jsonify, Response
from services.anthropic_client import client

stream_bp = Blueprint('stream', __name__)

@stream_bp.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        def generate():
            with client.messages.stream(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {text}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500
