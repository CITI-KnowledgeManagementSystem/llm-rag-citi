from ..response import HTTPRequestException
from ...main import generation_llm
from ..util.document import retrieve_documents_from_vdb, document_to_embeddings
from ..util.llm import format_conversation_history, get_context
from ..constant.llm import PROMPT_TEMPLATE
from llama_index.core.llms import ChatMessage
import asyncio

async def question_answer(question: str, user_id: str, conversations_history: list,
                        #    background_tasks: BackgroundTasks,
                        hyde: bool = False, reranking: bool = False):
    if not question or not user_id:
        raise HTTPRequestException(message="Please provide both question & user_id", status_code=400)
    
    try:
        # add history handler
        formatted_history = format_conversation_history(conversations_history if conversations_history else [])
        # getting context (hyde)
        if hyde == True:
            context = await get_context(question)
        else:
            context = question
            
        # print('context ==', context)

        # context retrieval with reranking option
        # question_embeddings = document_to_embeddings(context)
        question_embeddings = document_to_embeddings(context)
        private_documents = retrieve_documents_from_vdb(
                                embeddings=question_embeddings["dense"], 
                                user_id=user_id, 
                                collection_name='private', 
                                reranking=reranking,
                                query=question,
                                sparse_embeddings=question_embeddings["sparse"]
                            )
        public_documents = retrieve_documents_from_vdb(
                                embeddings=question_embeddings["dense"], 
                                collection_name='public', 
                                reranking=reranking,
                                query=question,
                                sparse_embeddings=question_embeddings["sparse"]
                            )
     
        context_snippets = []

        private_docs_labeled = [{**doc['entity'], 'source': 'Private'} for doc in private_documents]
        public_docs_labeled = [{**doc['entity'], 'source': 'Public'} for doc in public_documents]

       
        all_documents = private_docs_labeled + public_docs_labeled

        # 3. Sekarang, cara nampilinnya jadi lebih kaya
        # print("\n--- HASIL PENCARIAN DOKUMEN ---")
        for idx, doc in enumerate(all_documents):
            # Ambil semua data dari tiap 'doc'
            doc_content = doc.get('content', 'N/A')
            doc_name = doc.get('document_name', 'N/A')
            doc_page = doc.get('page_number', 'N/A')
            doc_source = doc.get('source', 'N/A')

            # print("-------------------------------------")
            # print(f"Kutipan Relevan #{idx + 1}")
            # print(f"\nIsi Kutipan:\n{doc_content}\n")
           
            # print(f"Sumber: {doc_name} (Halaman: {doc_page}) [Koleksi: {doc_source}]") 
            # print("-------------------------------------")

            # 2. Format tiap dokumen jadi blok teks yang rapi
            snippet = (
                f"Sumber Informasi:\n"
                f"  - Dokumen: {doc_name}\n"
                f"  - Halaman: {doc_page}\n"
                f"  - Koleksi: {doc_source}\n"
                f"Isi Kutipan:\n"
                f"\"{doc_content}\""
            )
            context_snippets.append(snippet)


        # Membuat messages dalam format yang sesuai dengan llama_index

        final_context_string = "\n\n---\n\n".join(context_snippets)
        messages = [
            ChatMessage(role="system", content=PROMPT_TEMPLATE.format(context=final_context_string)),
            ChatMessage(role="user", content=question)
        ]

    
        # Perubahan pada pemanggilan LLM
        response = await generation_llm.achat(messages)
        final_answer = response.message.content
        # print ("[LLM Service] Jawaban dari LLM:", final_answer)
        docs_to_return = []
        for doc in all_documents:
            docs_to_return.append({
                "document_id": doc.get('document_id'),
                "content": doc.get('content'),
                "document_name": doc.get('document_name'),
                "page_number": doc.get('page_number'),
                "source": doc.get('source')
            })
        return final_answer, docs_to_return

    
    except Exception as e:
        print("ERROOOOORRRRRRRRRRRR", e)
        raise HTTPRequestException(message=str(e), status_code=500)

def Streaming(question: str, user_id: str, conversations_history: list,
                        hyde: bool = False, reranking: bool = False):
    if not question or not user_id:
        raise HTTPRequestException(message="Please provide both question & user_id", status_code=400)

    try:

        formatted_history = format_conversation_history(conversations_history if conversations_history else [])
        if hyde:
            context = asyncio.run(get_context(question)) # get_context harus synchronous atau di-await dengan cara lain
        else:
            context = question

        print('context ==', context)

        question_embeddings = document_to_embeddings(context)
        private_documents = retrieve_documents_from_vdb(
                                embeddings=question_embeddings["dense"],
                                user_id=user_id,
                                collection_name='private',
                                reranking=reranking,
                                query=question,
                                sparse_embeddings=question_embeddings["sparse"]
                            )
        public_documents = retrieve_documents_from_vdb(
                                embeddings=question_embeddings["dense"],
                                collection_name='public',
                                reranking=reranking,
                                query=question,
                                sparse_embeddings=question_embeddings["sparse"]
                            )

        private_docs_labeled = [{**doc['entity'], 'source': 'Private'} for doc in private_documents]
        public_docs_labeled = [{**doc['entity'], 'source': 'Public'} for doc in public_documents]
        all_documents = private_docs_labeled + public_docs_labeled


        for doc in all_documents:
            # Cek dulu kalo 'content' ada dan tipenya string, buat jaga-jaga
            if 'content' in doc and isinstance(doc['content'], str):
                # Ganti semua karakter " di dalem konten jadi \"
                doc['content'] = doc['content'].replace('"', '\\"')
        context_snippets = []
        for doc in all_documents:
            snippet = (
                f"Sumber Informasi:\n"
                f"  - Dokumen: {doc.get('document_name', 'N/A')}\n"
                f"  - Halaman: {doc.get('page_number', 'N/A')}\n"
                f"  - Koleksi: {doc.get('source', 'N/A')}\n"
                f"Isi Kutipan:\n"
                f"\"{doc.get('content', 'N/A')}\""
            )
            context_snippets.append(snippet)


        final_context_string = "\n\n---\n\n".join(context_snippets)
        messages = [
            ChatMessage(role="system", content=PROMPT_TEMPLATE.format(context=final_context_string)),
            ChatMessage(role="user", content=question)
        ]
        # 1. Streaming response dari LLM
        streaming_response = generation_llm.stream_chat(messages)

        # 2. Ambil ID dokumen yang relevan

        retrieved_docs = all_documents  

        # 3. Kembalikan stream dan ID dokumen
        # Kita tidak lagi mengembalikan 'final_answer' dari sini
        return streaming_response, retrieved_docs


    except Exception as e:
        print("ERROOOOORRRRRRRRRRRR", e)
        raise HTTPRequestException(message=str(e), status_code=500)