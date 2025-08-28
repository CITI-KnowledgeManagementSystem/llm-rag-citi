from flask import request, jsonify, Response, stream_with_context
from ..service.llm_service import Streaming, agent_search
from ..service.evaluate import evaluate_single_turn_rag
import threading
from ..response import HTTPRequestException, HTTPRequestSuccess
from ...main import semaphore
import json

def chat_with_llm():    
    semaphore.acquire()
    body = request.get_json()
    question = body.get('question')
    conversation_history = body.get('conversation_history')
    hyde = body.get('hyde')
    hyde = True if hyde == 'true' else False
    reranking = body.get('reranking')
    reranking = True if reranking == 'true' else False
    user_id = body.get('userId')
    document_ids = body.get('document_ids', None)  # Bisa None atau list of strings
    print(body)
    print(hyde, reranking)

    try:
        llm_stream, retrieved_docs = Streaming(
            question=question, 
            user_id=user_id, 
            conversations_history=conversation_history, 
            document_ids=document_ids,
            hyde=hyde, 
            reranking=reranking
        )
        

        # Buat sebuah "inner function" (generator) untuk format SSE
        def generate_chunks():
            try:
                # 1. Kirim ID dokumen sebagai event pertama (opsional, tapi berguna!)
                # Ini memastikan frontend tahu sumbernya sebelum jawaban muncul
                for doc in retrieved_docs:
                    doc_payload = json.dumps({"retrieved_doc": doc})
                    yield f"data: {doc_payload}\n\n"
                # 2. Loop melalui stream dari LLM
                for chunk in llm_stream:
                    # 'chunk.delta' berisi potongan teks baru
                    token = chunk.delta
                    if token:
                        # Kirim setiap token dalam format Server-Sent Events (SSE)
                        # Format "data: [your_data]\n\n" adalah standar SSE
                        data_payload = json.dumps({"answer_token": token})
                        yield f"data: {data_payload}\n\n"
                
                # Opsional: Kirim sinyal bahwa stream sudah selesai
                yield f"data: [DONE]\n\n"

            except Exception as e:
                print(f"Error during streaming: {e}")
            finally:
                semaphore.release() # Pastikan semaphore dilepas di akhir stream
                
        return Response(stream_with_context(generate_chunks()), mimetype='text/event-stream')

    except HTTPRequestException as e:
        semaphore.release() # Pastikan semaphore dilepas jika ada error di awal
        return e.to_response()


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
