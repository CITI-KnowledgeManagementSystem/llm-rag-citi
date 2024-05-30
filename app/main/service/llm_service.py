import requests

from ..response import HTTPRequestException
from ..util.document import retrieve_documents_from_vdb, document_to_embeddings
from ..constant.llm import PROMPT_TEMPLATE, MODEL, TEMPERATURE, MAX_TOKENS, IS_STREAM, LLM_URL

dummy_history = []

def question_answer(question:str, collection_name:str, conversations_history:list=None):
    global dummy_history
    if not question or not collection_name:
        raise HTTPRequestException(message="Please provide both question and collection name", status_code=400)
    
    try:

        # add history handler
        

        # context retrieval
        question_embeddings = document_to_embeddings(question)
        documents = retrieve_documents_from_vdb(question_embeddings, collection_name)

        messages = [
            { 
                "role": "system", 
                "content": PROMPT_TEMPLATE.format(question=question, context=documents, history=dummy_history) 
            }
        ]
        
        content_body = {
            "model": MODEL,
            "messages": messages
        }

    
        res = requests.post(LLM_URL, json=content_body).json()
        
        dummy_history = dummy_history + [
            {
                "role": "user", "content": question
            },
            {
                "role": "assistant", "content": res['choices'][0]['message']['content']
            }
        ]

        with open(r"C:\Users\CITI-AI\llm-rag-citi\test.md", 'w') as f:
            f.write(res['choices'][0]['message']['content'])

        return res['choices'][0]['message']['content']
    
    except Exception as e:
        raise HTTPRequestException(message=str(e), status_code=500)

