from flask import Blueprint
from ..controller.llm import *


blueprint = Blueprint('llm', __name__, url_prefix='/llm')

@blueprint.route('/chat_with_llm', methods=['POST'])
async def chat_with_llm_route():
    await chat_with_llm()

