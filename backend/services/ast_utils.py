import ast

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