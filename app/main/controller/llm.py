from flask import request, jsonify, Response, stream_with_context
from ..service.llm_service import question_answer, Streaming, agent_search
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
    print(body)
    print(hyde, reranking)

    try:
        llm_stream, retrieved_docs = Streaming(
            question, user_id, conversation_history, hyde, reranking
        )
        
        #  response_payload = {
        #     "answer": final_answer,
        #     "retrieved_docs": all_documents  # <-- Kunci baru, isinya list dokumen
        # }
        
        # print("[Controller] Jawaban siap. Menjadwalkan evaluasi di background thread...")
        # retrieved_contexts_list = [doc.get('content', 'N/A') for doc in retrieved_docs]

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


# async def chat_with_llm():    
#     semaphore.acquire()
#     body = request.get_json()
#     question = body.get('question')
#     conversation_history = body.get('conversation_history')
#     hyde = body.get('hyde', 'false').lower() == 'true'
#     reranking = body.get('reranking', 'false').lower() == 'true'
#     user_id = body.get('userId')

#     try:
#         print(body)
#         print(f"HyDE: {hyde}, Reranking: {reranking}")

#         # Panggil service yang balikin generator dan dokumen
#         llm_stream, retrieved_docs = await agent_search(
#             question, user_id, conversation_history, hyde, reranking
#         )
        
#         # Kita bikin generator function buat ngirim data ke client
#         def generate_stream():
#             try:
#                 print("Starting stream generation... sini boi")
#                 # 1. Kirim source documents dulu sebagai event pertama
#                 # Ini biar UI bisa nampilin sumbernya duluan
#                 source_event = {
#                     "sources": retrieved_docs
#                 }
#                 # Format Server-Sent Event (SSE): 'data: {json}\n\n'
#                 yield f"data: {json.dumps(source_event)}\n\n"

#                 # 2. Iterasi stream dari agent dan kirim token satu per satu
#                 for delta in llm_stream.response_gen:
#                     # Setiap delta adalah token baru
#                     token_event = {
#                         "token": delta
#                     }
#                     yield f"data: {json.dumps(token_event)}\n\n"
            
#             except Exception as e:
#                 # Kalo ada error di tengah jalan streaming
#                 print(f"Error during stream generation: {e}")
#                 error_event = {
#                     "error": "An error occurred during streaming."
#                 }
#                 yield f"data: {json.dumps(error_event)}\n\n"

#         # Balikin Response object dengan generator kita.
#         # mimetype='text/event-stream' ini wajib buat streaming (SSE)
#         return Response(generate_stream(), mimetype='text/event-stream')

#         # return Response(llm_stream, mimetype='text/event-stream')

#     except Exception as e:
#         # Error handling sebelum streaming dimulai
#         print(f"Error in chat_with_llm endpoint: {e}")
#         return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')
    
#     finally:
#         # PENTING: Selalu release semaphore, gak peduli sukses atau gagal
#         semaphore.release()

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
