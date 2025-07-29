# from langchain.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser

from ...main import hyde_llm
from ..constant.llm import HYDE_PROMPT_TEMPLATE

from llama_index.core import PromptTemplate

# def get_context(question:str):
#     prompt_template = HYDE_PROMPT_TEMPLATE    
#     prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

#     llm_chain = prompt | hyde_llm | StrOutputParser()
#     print('question', question)
#     context = llm_chain.ainvoke({'question':question, 'stream': False})
#     return context

async def get_context(question:str):
    prompt_template = PromptTemplate(HYDE_PROMPT_TEMPLATE)
    
    response = await hyde_llm.acomplete(prompt_template.format(question=question))
    return response.text


def format_conversation_history(history:list):
    new_hist = []
    for message in history:
        if message["type"] == "request":
            new_hist.append(
                {
                    "role": "user",
                    "content": message["message"]
                }
            )
        else:
            new_hist.append(
                {
                    "role": "assistant",
                    "content": message["message"]
                }
            )
    return new_hist