from flask import Blueprint, request, jsonify
from services.anthropic_client import client

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
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
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=messages
        )
        
        assistant_message = response.content[0].text
        
        return jsonify({
            "response": assistant_message,
            "success": True
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500
