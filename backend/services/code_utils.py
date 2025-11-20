from pygments.lexers import guess_lexer

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
