from ..response import HTTPRequestException
from ...main import generation_llm
from ..util.document import retrieve_documents_from_vdb, document_to_embeddings_bge_m3
from ..util.llm import format_conversation_history, get_context
from ..constant.llm import PROMPT_TEMPLATE


async def question_answer(question: str, user_id: str, conversations_history: list, 
                        hyde: bool = False, reranking: bool = False):
    print(user_id)
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
            
        print('context ==', context)

        # context retrieval with reranking option
        # question_embeddings = document_to_embeddings(context)
        question_embeddings = document_to_embeddings_bge_m3(context)
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
        # get content from each doc
        content = []
        for doc in private_documents:
            content.append(doc.get('content'))
        for doc in public_documents:
            content.append(doc.get('content'))
        print('content', content)

        # Membuat messages dalam format yang sesuai dengan llama_index

        
        from llama_index.core.llms import ChatMessage, TextBlock, ImageBlock
        from llama_index.llms.openai import OpenAI
        
        messages = [
            ChatMessage(role="system", content=PROMPT_TEMPLATE.format(context=content)),
            ChatMessage(role="user", content=question)
        ]
        print("\n\n\nmessages", messages)

    
        # Perubahan pada pemanggilan LLM
        response = await generation_llm.achat(messages)
        return response.message.content
    
    except Exception as e:
        print(e)
        raise HTTPRequestException(message=str(e), status_code=500)

