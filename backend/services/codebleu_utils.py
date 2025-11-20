from flask import request, jsonify
from codebleu import calc_codebleu

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