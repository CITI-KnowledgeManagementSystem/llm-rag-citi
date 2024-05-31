from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

def get_context(question:str):
    prompt_template = """
    You are a helpful AI assistant. Please give context to the user's question based on your knowledge.
    The response should be an explanation of the user's question, not the answer of the question.
    Another criteria is that the response should not specify which time period the information is from. 
    Question: {question}
    """
            
    prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

    llm = ChatOpenAI(
        openai_api_base = "http://140.118.101.189:8080/v1",
        model_name = "gpt-4",
        n=3,
        temperature=1,
    )

    llm_chain = prompt | llm | StrOutputParser()
    
    context = llm_chain.invoke({'question':question})
    # context = question

    # print(type(prompt))
    # prompt = prompt.invoke({'question':'Tell me the history of USA.', 'context':''})
    
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