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

def detect_language(code):
    code = code.strip()
    
    if not code:
        return 'python'
    
    scores = {
        'python': 0,
        'java': 0,
        'javascript': 0,
        'cpp': 0,
        'c': 0,
        'rust': 0,
        'go': 0,
        'php': 0,
        'ruby': 0,
        'c_sharp': 0
    }
    
    code_lower = code.lower()
    
    if 'public class' in code:
        scores['java'] += 10
    if 'public static' in code:
        scores['java'] += 10
    if 'private ' in code or 'protected ' in code:
        scores['java'] += 5
    if 'void ' in code or 'int ' in code or 'String ' in code:
        scores['java'] += 3
    if 'System.' in code:
        scores['java'] += 8
    if 'Arrays.' in code or '.length' in code:
        scores['java'] += 3
    if code.count(';') > 2:
        scores['java'] += 2
        scores['cpp'] += 2
        scores['c'] += 2
        scores['javascript'] += 1
    
    if 'def ' in code and ':' in code:
        scores['python'] += 10
    if 'import ' in code and 'from ' in code:
        scores['python'] += 8
    if code.count(':') > 2 and code.count('{') == 0:
        scores['python'] += 5
    if 'self' in code or '__init__' in code:
        scores['python'] += 8
    if code.count('    ') > 3:
        scores['python'] += 3
    
    if 'function' in code_lower:
        scores['javascript'] += 8
        scores['php'] += 3
    if 'const ' in code or 'let ' in code or 'var ' in code:
        scores['javascript'] += 10
    if '=>' in code:
        scores['javascript'] += 8
    if 'console.log' in code:
        scores['javascript'] += 10
    
    if '#include' in code:
        scores['cpp'] += 8
        scores['c'] += 8
    if 'std::' in code or 'cout' in code or 'endl' in code:
        scores['cpp'] += 10
        scores['c'] = 0
    if 'namespace' in code or 'using namespace' in code:
        scores['cpp'] += 10
        scores['c'] = 0
    if 'printf' in code or 'scanf' in code:
        scores['c'] += 8
    if 'int main()' in code or 'int main(' in code:
        scores['cpp'] += 5
        scores['c'] += 5
    
    if '<?php' in code:
        scores['php'] += 15
    if '$' in code and 'function' in code_lower:
        scores['php'] += 8
    
    if 'fn main' in code or 'fn ' in code:
        scores['rust'] += 10
    if 'let mut' in code:
        scores['rust'] += 10
    
    if 'func main' in code or 'package main' in code:
        scores['go'] += 10
    if 'fmt.' in code:
        scores['go'] += 8
    
    if 'using System' in code or 'namespace ' in code and 'class' in code:
        scores['c_sharp'] += 10
    
    max_score = max(scores.values())
    
    if max_score > 5:
        detected = max(scores, key=scores.get)
        print(f"Language detection scores: {scores}")
        print(f"Detected language: {detected} (score: {max_score})")
        return detected
    
    try:
        lexer = guess_lexer(code)
        lang_name = lexer.name.lower()
        
        print(f"Pygments detected: {lang_name}")
        
        if 'python' in lang_name:
            return 'python'
        elif 'java' in lang_name and 'javascript' not in lang_name:
            return 'java'
        elif 'javascript' in lang_name or 'ecmascript' in lang_name:
            return 'javascript'
        elif 'c++' in lang_name or 'cpp' in lang_name:
            return 'cpp'
        elif 'c' in lang_name and 'c++' not in lang_name:
            return 'c'
        
    except Exception as e:
        print(f"Pygments error: {e}")
    
    print(f"Defaulting to python. Scores were: {scores}")
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
                "method": "Python AST",
                "ast": ast_dict
            }
        else:
            ts_ast = generate_tree_sitter_ast(code, language)
            if ts_ast:
                return ts_ast
            
            return {
                "supported": False,
                "language": language,
                "message": f"AST generation for {language} is not available. Supported: Python, Java, JavaScript, C, C++."
            }
    except Exception as e:
        return {
            "supported": False,
            "error": str(e),
            "message": f"Failed to generate AST: {str(e)}"
        }

def generate_tree_sitter_ast(code, language):
    try:
        from tree_sitter import Language, Parser
        
        lang_module_map = {
            'java': 'tree_sitter_java',
            'javascript': 'tree_sitter_javascript',
            'c': 'tree_sitter_c',
            'cpp': 'tree_sitter_cpp',
            'c_sharp': 'tree_sitter_c_sharp',
        }
        
        if language not in lang_module_map:
            return None
        
        module_name = lang_module_map[language]
        lang_module = __import__(module_name)
        
        parser = Parser()
        ts_language = Language(lang_module.language())
        parser.set_language(ts_language)
        
        tree = parser.parse(bytes(code, 'utf8'))
        root = tree.root_node
        
        ast_dict = tree_sitter_node_to_dict(root, code)
        
        return {
            "supported": True,
            "language": language,
            "method": "Tree-sitter",
            "ast": ast_dict
        }
        
    except ImportError as e:
        print(f"Tree-sitter module not found for {language}: {e}")
        return None
    except Exception as e:
        print(f"Error generating tree-sitter AST for {language}: {e}")
        return None

def tree_sitter_node_to_dict(node, code_bytes):
    if isinstance(code_bytes, str):
        code_bytes = code_bytes.encode('utf8')
    
    result = {
        "type": node.type,
        "start": {"row": node.start_point[0], "column": node.start_point[1]},
        "end": {"row": node.end_point[0], "column": node.end_point[1]},
    }
    
    if node.child_count == 0:
        text = code_bytes[node.start_byte:node.end_byte].decode('utf8')
        if text.strip():
            result["text"] = text
    else:
        result["children"] = [tree_sitter_node_to_dict(child, code_bytes) for child in node.children]
    
    return result

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

