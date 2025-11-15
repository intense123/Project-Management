from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv
import ast
import json
from pygments.lexers import get_lexer_by_name, guess_lexer
from codebleu import calc_codebleu
import astpretty

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables. Please set it in the .env file.")

client = anthropic.Anthropic(api_key=api_key)

CODE_GENERATION_PROMPT = """You are a code generation AI. 

CRITICAL RULES - FOLLOW EXACTLY:
1. Generate ONLY code - absolutely NO explanations, NO markdown, NO comments, NO text before or after
2. Start directly with the code itself
3. Do NOT wrap code in markdown code blocks or backticks
4. Do NOT include phrases like "Here's the code" or "This code does..."
5. Output ONLY the raw code that was requested
6. Ensure code is syntactically correct and follows best practices

Example:
User: "Python function for fibonacci"
You: def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

User: "Java calculator class"
You: public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    public int subtract(int a, int b) {
        return a - b;
    }
}

REMEMBER: Only code, nothing else."""

def detect_language(code):
    code_lower = code.lower().strip()
    
    if 'def ' in code or 'import ' in code or 'print(' in code or code.startswith('class ') and ':' in code:
        return 'python'
    elif 'public class' in code or 'public static void main' in code or 'System.out.println' in code:
        return 'java'
    elif 'function ' in code or 'const ' in code or 'let ' in code or 'var ' in code or 'console.log' in code:
        return 'javascript'
    elif '#include' in code and ('int main' in code or 'std::' in code or 'cout' in code):
        return 'cpp'
    elif '#include' in code and 'printf' in code:
        return 'c'
    elif 'fn main' in code or 'let mut' in code:
        return 'rust'
    elif 'func main' in code or 'package main' in code:
        return 'go'
    elif '<?php' in code or 'function ' in code and '$' in code:
        return 'php'
    elif 'def ' in code_lower and 'end' in code_lower:
        return 'ruby'
    
    try:
        lexer = guess_lexer(code)
        lang_name = lexer.name.lower()
        if 'python' in lang_name:
            return 'python'
        elif 'java' in lang_name and 'javascript' not in lang_name:
            return 'java'
        elif 'javascript' in lang_name or 'js' in lang_name:
            return 'javascript'
        elif 'c++' in lang_name or 'cpp' in lang_name:
            return 'cpp'
        elif 'c#' in lang_name or 'csharp' in lang_name:
            return 'c_sharp'
        elif lang_name == 'c':
            return 'c'
        elif 'rust' in lang_name:
            return 'rust'
        elif 'go' in lang_name:
            return 'go'
        elif 'php' in lang_name:
            return 'php'
        elif 'ruby' in lang_name:
            return 'ruby'
    except:
        pass
    
    return 'python'

def get_file_extension(language):
    extensions = {
        'python': '.py',
        'java': '.java',
        'javascript': '.js',
        'typescript': '.ts',
        'c++': '.cpp',
        'cpp': '.cpp',
        'c': '.c',
        'go': '.go',
        'rust': '.rs',
        'php': '.php',
        'ruby': '.rb',
        'swift': '.swift',
        'kotlin': '.kt',
        'csharp': '.cs',
        'c_sharp': '.cs',
    }
    return extensions.get(language.lower(), '.py')

def generate_ast(code, language):
    try:
        if language == 'python':
            tree = ast.parse(code)
            ast_dict = ast_to_dict(tree)
            return {
                "supported": True,
                "language": "python",
                "ast": ast_dict
            }
        else:
            return {
                "supported": False,
                "language": language,
                "message": f"AST generation currently supports Python only. {language} support is not yet available."
            }
    except Exception as e:
        return {
            "supported": False,
            "error": str(e),
            "message": f"Failed to generate AST: {str(e)}"
        }

def ast_to_dict(node):
    if isinstance(node, ast.AST):
        result = {"type": node.__class__.__name__}
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                result[field] = [ast_to_dict(item) for item in value]
            elif isinstance(value, ast.AST):
                result[field] = ast_to_dict(value)
            else:
                result[field] = value
        return result
    return node

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running!"})

@app.route('/api/chat', methods=['POST'])
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

@app.route('/api/chat/code', methods=['POST'])
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

def normalize_language_for_codebleu(language):
    lang_map = {
        'python': 'python',
        'java': 'java',
        'javascript': 'javascript',
        'js': 'javascript',
        'cpp': 'cpp',
        'c++': 'cpp',
        'c': 'c',
        'csharp': 'c_sharp',
        'c_sharp': 'c_sharp',
        'c#': 'c_sharp',
        'php': 'php',
        'go': 'go',
        'ruby': 'ruby',
        'rust': 'rust'
    }
    normalized = lang_map.get(language.lower(), 'python')
    
    supported_langs = ['java', 'javascript', 'c_sharp', 'php', 'c', 'cpp', 'python', 'go', 'ruby', 'rust']
    if normalized not in supported_langs:
        normalized = 'python'
    
    return normalized

@app.route('/api/evaluate/codebleu', methods=['POST'])
def evaluate_codebleu():
    try:
        data = request.json
        generated_code = data.get('generated_code', '')
        reference_code = data.get('reference_code', '')
        language = data.get('language', 'python')
        
        if not generated_code or not reference_code:
            return jsonify({"error": "Both generated and reference code are required"}), 400
        
        generated_code = str(generated_code).strip()
        reference_code = str(reference_code).strip()
        
        if not generated_code or not reference_code:
            return jsonify({"error": "Code cannot be empty after stripping whitespace"}), 400
        
        normalized_lang = normalize_language_for_codebleu(language)
        
        print(f"Evaluating CodeBLEU for language: {normalized_lang}")
        print(f"Generated code length: {len(generated_code)}")
        print(f"Reference code length: {len(reference_code)}")
        
        try:
            result = calc_codebleu(
                references=[[reference_code]],
                predictions=[generated_code],
                lang=normalized_lang,
                weights=(0.25, 0.25, 0.25, 0.25),
                tokenizer=None
            )
        except Exception as calc_error:
            print(f"CodeBLEU calculation error: {str(calc_error)}")
            print(f"Error type: {type(calc_error).__name__}")
            
            if "Tree-sitter" in str(calc_error) or "tree-sitter" in str(calc_error):
                return jsonify({
                    "error": f"Tree-sitter parser for {normalized_lang} not properly installed. Please run: pip install tree-sitter-{normalized_lang}",
                    "success": False
                }), 500
            
            return jsonify({
                "error": f"Error calculating CodeBLEU: {str(calc_error)}. Using simpler metrics instead.",
                "codebleu_score": 0.0,
                "ngram_match_score": 0.0,
                "weighted_ngram_match_score": 0.0,
                "syntax_match_score": 0.0,
                "dataflow_match_score": 0.0,
                "language_used": normalized_lang,
                "success": False
            }), 500
        
        return jsonify({
            "codebleu_score": float(result.get('codebleu', 0.0)),
            "ngram_match_score": float(result.get('ngram_match_score', 0.0)),
            "weighted_ngram_match_score": float(result.get('weighted_ngram_match_score', 0.0)),
            "syntax_match_score": float(result.get('syntax_match_score', 0.0)),
            "dataflow_match_score": float(result.get('dataflow_match_score', 0.0)),
            "language_used": normalized_lang,
            "success": True
        })
        
    except Exception as e:
        print(f"Error in CodeBLEU evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/chat/stream', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)

