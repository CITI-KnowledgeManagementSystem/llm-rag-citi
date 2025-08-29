from flask import request, jsonify, Response, stream_with_context
from ..service.llm_service import question_answer, Streaming, agent_search, regenerate_mind_map_service, generate_title

from ..service.evaluate import evaluate_single_turn_rag
import threading
from ..response import HTTPRequestException, HTTPRequestSuccess
from ...main import semaphore
import json
from llama_index.core.agent.workflow import AgentStream
import asyncio

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


# def chat_with_llm():    
#     semaphore.acquire()
#     body = request.get_json()
#     question = body.get('question')
#     conversation_history = body.get('conversation_history')
#     hyde = body.get('hyde', 'false').lower() == 'true'
#     reranking = body.get('reranking', 'false').lower() == 'true'
#     user_id = body.get('userId')

#     try:
#         # Panggil fungsi SINKRON kita yang baru
#         llm_stream_generator, retrieved_docs = agent_search(
#             question, user_id, conversation_history, hyde, reranking
#         )
        
#         def generate_chunks():
#             try:
#                 # 1. Kirim dokumen dulu
#                 source_event = {"sources": retrieved_docs}
#                 yield f"data: {json.dumps(source_event)}\n\n"
                
#                 # 2. Loop melalui stream SINKRON dari agent
#                 for event in llm_stream_generator:
#                     # Pastiin event-nya tipe yang bener
#                     if isinstance(event, AgentStream):
#                         token = event.delta
#                         if token:
#                             data_payload = json.dumps({"answer_token": token})
#                             yield f"data: {data_payload}\n\n"
                
#                 yield f"data: [DONE]\n\n"

#             except Exception as e:
#                 print(f"Error during streaming generation: {e}")
#             finally:
#                 semaphore.release()
                
#         return Response(stream_with_context(generate_chunks()), mimetype='text/event-stream')

#     except HTTPRequestException as e:
#         semaphore.release()
#         return e.to_response()
#     except Exception as e:
#         # Fallback error handler
#         semaphore.release()
#         return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

async def create_title():  
    body = request.get_json()
    prompt = body.get('prompt')

    try:
        # Panggil service yang baru kita buat
        title = await generate_title(prompt)
        
        # Kirim response sukses dengan payload berisi judul
        return HTTPRequestSuccess(
            message="Title generated successfully", 
            status_code=200, 
            payload={"title": title}
        ).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
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
    
async def regenerate_mind_map():
    body = request.get_json()
    question = body.get('question')
    # hyde = body.get('hyde')
    # hyde = True if hyde == 'true' else False
    # reranking = body.get('reranking')
    # reranking = True if reranking == 'true' else False
    user_id = body.get('user_id')
    
    # ====== Testing ======
    # question = "make a mindmap about Cycling Learning Rate"
    # user_id = "user_2yfckZL2Y68NPUyEMOMy456sBWD"
    hyde = True
    reranking = True
    
    try:
        res = await regenerate_mind_map_service(
            question, user_id, hyde, reranking
        )
        
        print('res ==', res)
        
        return HTTPRequestSuccess(message="Mind map regenerated", status_code=200, payload=res).to_response()
    
    except HTTPRequestException as e:
        print(e.message)
        return e.to_response()
