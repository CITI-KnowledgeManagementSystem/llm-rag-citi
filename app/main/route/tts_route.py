from flask import Blueprint
from ..controller.tts import *


blueprint = Blueprint('tts', __name__, url_prefix='/tts')

# Custom TTS endpoint
blueprint.route('/generate', methods=['POST'])(generate_tts)

# OpenAI-compatible TTS endpoint
blueprint.route('/v1/audio/speech', methods=['POST'])(generate_tts_openai)

# Podcast generation endpoint (RAG + TTS)
blueprint.route('/podcast', methods=['POST'])(generate_podcast)

# Conversational podcast endpoint (NotebookLM style)
blueprint.route('/podcast/conversational', methods=['POST'])(generate_conversational_podcast_endpoint)

# Audio file download endpoint
blueprint.route('/download', methods=['GET'])(download_audio)