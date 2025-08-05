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
    # print(body)
    # print(hyde, reranking)

    try:
        # Panggil service lo seperti biasa untuk dapet jawaban
        print("[Controller] Request chat dengan LLM...")
        final_answer, all_documents = await question_answer(
            question, user_id, conversation_history, hyde, reranking
        )
        response_payload = {
            "answer": final_answer,
            "retrieved_docs": all_documents  # <-- Kunci baru, isinya list dokumen
        }
        
        # print("[Controller] Jawaban siap. Menjadwalkan evaluasi di background thread...")
        retrieved_contexts_list = [doc.get('content', 'N/A') for doc in all_documents]
        
        # Bikin thread baru
        # eval_thread = threading.Thread(
        #     target=evaluate_single_turn_rag, # <-- Targetnya fungsi SYNC
        #     args=(question, final_answer, retrieved_contexts_list) # <-- Argumennya
        # )
        
        # # Suruh thread-nya mulai kerja (Fire and Forget)
        # eval_thread.start()

        # Controller langsung kirim jawaban ke user
        return HTTPRequestSuccess(message="Success", status_code=200, payload=response_payload).to_response() 

    except HTTPRequestException as e:
        return e.to_response()
    
    finally:
        semaphore.release()

def evaluate_chat():
    try:
        body = request.get_json()
        message_id = body.get('message_id')
        question = body.get('question')
        answer = body.get('answer')
        contexts = body.get('contexts')

        # Validasi input...
        if not all([message_id, question, answer, contexts]):
            return jsonify({"error": "Missing required fields"}), 400

        # Jalankan di background thread
        eval_thread = threading.Thread(
            target=evaluate_single_turn_rag,
            args=(message_id, question, answer, contexts)
        )
        eval_thread.start()

        return jsonify({"status": "Evaluation scheduled"}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500
