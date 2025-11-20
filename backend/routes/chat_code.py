from flask import Blueprint, request, jsonify
from services.anthropic_client import client
from services.code_utils import detect_language, get_file_extension
from services.ast_utils import generate_ast

chat_code_bp = Blueprint('chat_code', __name__)

CODE_GENERATION_PROMPT = """You are a precise code generation AI. 

CRITICAL RULES - FOLLOW EXACTLY:
1. Generate ONLY code - absolutely NO explanations, NO markdown, NO comments, NO text before or after
2. Start directly with the code itself
3. Do NOT wrap code in markdown code blocks or backticks
4. Do NOT include phrases like "Here's the code" or "This code does..."
5. Output ONLY the raw code that was requested
6. Ensure code is syntactically correct and follows best practices
7. Pay CLOSE ATTENTION to the programming language requested by the user
8. If user says "function", generate ONLY that function
9. If user says "class", generate the complete class
10. If user says "program" or "full code", generate complete working code with all necessary imports

Language-specific rules:
- Python: Use proper indentation, include necessary imports
- Java: Include proper class declaration with main method if needed
- JavaScript: Use modern ES6+ syntax
- C/C++: Include necessary headers and main function if needed
- Other languages: Follow standard conventions

Examples:
User: "Python function for fibonacci"
You: def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

User: "Java function for sorting array"
You: public static void sortArray(int[] arr) {
    Arrays.sort(arr);
}

User: "Complete Java class for calculator"
You: public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
    
    public double divide(int a, int b) {
        if (b == 0) throw new ArithmeticException("Division by zero");
        return (double) a / b;
    }
}

REMEMBER: Only code, nothing else. Match the requested language EXACTLY."""

@chat_code_bp.route('/api/chat/code', methods=['POST'])
def chat_code():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        messages = []
        
        for msg in conversation_history:
            if msg.get('role') == 'user':
                messages.append({
                    "role": "user",
                    "content": msg["content"]
                })
            elif msg.get('role') == 'assistant':
                messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })
        
        messages.append({
            "role": "user",
            "content": f"{CODE_GENERATION_PROMPT}\n\nUser request: {user_message}"
        })
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            messages=messages,
            temperature=0
        )
        
        generated_code = response.content[0].text.strip()
        
        language = detect_language(generated_code)
        file_extension = get_file_extension(language)
        
        ast_data = generate_ast(generated_code, language)
        
        return jsonify({
            "response": generated_code,
            "language": language,
            "file_extension": file_extension,
            "ast": ast_data,
            "success": True
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500
