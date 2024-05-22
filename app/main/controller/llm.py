from flask import request
from ..service.llm_service import question_answer
from ..response import HTTPRequestException, HTTPRequestSuccess

def chat_with_llm():
    body = request.get_json()
    question = body.get('question')
    conversation_history = body.get('conversation_history')

    try:
        res = question_answer(question, conversation_history)
        return HTTPRequestSuccess(message="Success", status_code=200, payload=res).to_response() 

    except HTTPRequestException as e:
        return e.to_response()

