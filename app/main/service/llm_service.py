<<<<<<< HEAD
import asyncio
import requests

=======
>>>>>>> c55edc0ef8d89d82d7707cf9c10d11433a2d80a0
from ..response import HTTPRequestException
from ...main import generation_llm
from ..util.document import retrieve_documents_from_vdb, document_to_embeddings
from ..util.llm import format_conversation_history, get_context
from ..constant.llm import PROMPT_TEMPLATE


async def question_answer(question:str, collection_name:str, conversations_history:list, hyde:bool=False, reranking:bool=False):
    if not question or not collection_name:
        raise HTTPRequestException(message="Please provide both question and collection name", status_code=400)
    
    try:
        # add history handler
        formatted_history = format_conversation_history(conversations_history if conversations_history else [])
        
        # getting context (hyde)
        if hyde == "True":
            context = await get_context(question)
        else:
            context = question


        # context retrieval with reranking option
        question_embeddings = document_to_embeddings(context)
        documents = retrieve_documents_from_vdb(question_embeddings, collection_name, reranking)
        
        # get content from each doc
        content = []
        for doc in documents:
            content.append(doc.get('content'))

        messages = [
            { 
                "role": "system", 
                "content": PROMPT_TEMPLATE.format(context=content) 
            }
        ] + formatted_history + [
            {
                "role": "user",
                "content": question
            }
        ]
    
<<<<<<< HEAD
        res = await asyncio.to_thread(requests.post(LLM_URL, json=content_body))
        res = res.json()
=======
        res = await generation_llm.ainvoke(messages)
>>>>>>> c55edc0ef8d89d82d7707cf9c10d11433a2d80a0

        return res.content
    
    except Exception as e:
        print(e)
        raise HTTPRequestException(message=str(e), status_code=500)

