from flask import request
from ..service.llm_service import question_answer
from ..response import HTTPRequestException, HTTPRequestSuccess
from ...main import semaphore

async def chat_with_llm():
    semaphore.acquire()
    body = request.get_json()
    question = body.get('question')
    collection_name = body.get('collection_name')
    conversation_history = body.get('conversation_history')
    hyde = body.get('hyde')
    hyde = True if hyde == 'true' else False
    reranking = body.get('reranking')
    reranking = True if reranking == 'true' else False
    print(hyde, reranking)

    try:
        res = await question_answer(question, collection_name, conversation_history, hyde, reranking)
        return HTTPRequestSuccess(message="Success", status_code=200, payload=res).to_response() 

    except HTTPRequestException as e:
        return e.to_response()
    
    finally:
        semaphore.release()

