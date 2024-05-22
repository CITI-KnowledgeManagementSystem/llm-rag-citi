import requests

from ..response import HTTPRequestException
from ..constant.llm import PROMPT_TEMPLATE, MODEL, TEMPERATURE, MAX_TOKENS, IS_STREAM, LLM_URL



def question_answer(question:str, conversations_history:list=None):

    if not question:
        raise HTTPRequestException(message="Please provide a question", status_code=400)
    
    # add history handler

    # messages = [{ "role": "system", "content": PROMPT_TEMPLATE }] + conversations_history if conversations_history else [] + [{ "role": "user", "content": question}]
    messages = conversations_history if conversations_history else [] + [{ "role": "user", "content": question}]
    
    content_body = {
        "model": MODEL,
        "messages": messages
    }

    try:
        res = requests.post(LLM_URL, data=content_body).json()

        with open(r"C:\Users\CITI-AI\llm-rag-citi\test.md", 'w') as f:
            f.write(res['choices'][0]['message']['content'])

        return res['choices'][0]['message']['content']
    
    except Exception as e:
        raise HTTPRequestException(message=str(e), status_code=500)

