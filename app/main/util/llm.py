from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ...main import llm

def get_context(question:str):
    prompt_template = """
    You are a helpful AI assistant. Please give context to the user's question based on your knowledge.
    The response should be an explanation of the user's question, not the answer of the question.
    Another criteria is that the response should not specify which time period the information is from. 
    Question: {question}
    """
            
    prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

    llm_chain = prompt | llm | StrOutputParser()
    
    context = llm_chain.invoke({'question':question})
    
    return context


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