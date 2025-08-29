from flask import Blueprint
from ..controller.llm import *


blueprint = Blueprint('llm', __name__, url_prefix='/llm')
blueprint.route('/chat_with_llm', methods=['POST'])(chat_with_llm)
blueprint.route('/evaluate', methods=['POST'])(evaluate_chat)
blueprint.route('/regenerate_mind_map', methods=['POST'])(regenerate_mind_map)
blueprint.route('/generate-title', methods=['POST'])(create_title)

