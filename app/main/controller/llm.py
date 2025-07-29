from flask import request, jsonify
from ..service.llm_service import question_answer
from ..service.evaluate import evaluate_single_turn_rag
import threading
from ..response import HTTPRequestException, HTTPRequestSuccess
from ...main import semaphore
import json

async def chat_with_llm():
    semaphore.acquire()
    body = request.get_json()
    question = body.get('question')
    conversation_history = json.loads(body.get('conversation_history'))
    hyde = body.get('hyde')
    hyde = True if hyde == 'true' else False
    reranking = body.get('reranking')
    reranking = True if reranking == 'true' else False
    user_id = body.get('user_id')
    print(body)
    print(hyde, reranking)

    try:
        # Panggil service lo seperti biasa untuk dapet jawaban
        print("[Controller] Menerima request chat dengan LLM...")
        final_answer, retrieved_doc_ids, all_documents = await question_answer(
            question, user_id, conversation_history, hyde, reranking
        )
        response_payload = {
            "answer": final_answer,
            "retrieved_doc_ids": retrieved_doc_ids # <-- Kunci baru, isinya list ID
        }
        
        # print("[Controller] Jawaban siap. Menjadwalkan evaluasi di background thread...")
        retrieved_contexts_list = [doc.get('content', 'N/A') for doc in all_documents]
        
        # Bikin thread baru
        eval_thread = threading.Thread(
            target=evaluate_single_turn_rag, # <-- Targetnya fungsi SYNC
            args=(question, final_answer, retrieved_contexts_list) # <-- Argumennya
        )
        
        # Suruh thread-nya mulai kerja (Fire and Forget)
        eval_thread.start()

        # Controller langsung kirim jawaban ke user
        return HTTPRequestSuccess(message="Success", status_code=200, payload=response_payload).to_response() 

    except HTTPRequestException as e:
        return e.to_response()
    
    finally:
        semaphore.release()
