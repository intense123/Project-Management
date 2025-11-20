from flask import Blueprint
from services.codebleu_utils import evaluate_codebleu

codebleu_bp = Blueprint('codebleu', __name__)

@codebleu_bp.route('/api/evaluate/codebleu', methods=['POST'])
def evaluate_codebleu_endpoint():
    return evaluate_codebleu()
