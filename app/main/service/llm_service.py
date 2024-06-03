import requests

from ..response import HTTPRequestException
from ..util.document import retrieve_documents_from_vdb, document_to_embeddings
from ..util.llm import format_conversation_history, get_context
from ..constant.llm import PROMPT_TEMPLATE, MODEL, TEMPERATURE, MAX_TOKENS, IS_STREAM, LLM_URL


def question_answer(question:str, collection_name:str, conversations_history:list, hyde:bool=False, reranking:bool=False):
    if not question or not collection_name:
        raise HTTPRequestException(message="Please provide both question and collection name", status_code=400)
    
    try:
        # add history handler
        formatted_history = format_conversation_history(conversations_history if conversations_history else [])
        
        # getting context (hyde)
        if hyde == "True":
            context = get_context(question)
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
        
        content_body = {
            "model": MODEL,
            "messages": messages
        }
    
        res = requests.post(LLM_URL, json=content_body).json()

        return res['choices'][0]['message']['content']
    
    except Exception as e:
        print(e)
        raise HTTPRequestException(message=str(e), status_code=500)

