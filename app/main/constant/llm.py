import os

LLM_URL = os.getenv('LLM_URL')
HYDE_LLM_URL = os.getenv('HYDE_LLM_URL')
HYDE_PROMPT_TEMPLATE = """
You are a helpful AI assistant. Please give context to the user's question based on your knowledge.
The response should be an explanation of the user's question, not the answer of the question.
Another criteria is that the response should not specify which time period the information is from. 
Question: {question}
"""
PROMPT_TEMPLATE = """
You are a helpful, respectful and honest assistant.
Always answer a question based on the INSTRUCTION.

INSTRUCTION: 
Answer the QUESTION using the CONTEXT provided below to answer user's question. If the question can't be answered, use your knowledge to answer the question.
You don't have to explain everything if there is an option to answer the question directly.

CONTEXT:
{context}
"""
MODEL = "gpt-4"
N_HYDE_INSTANCE = 1
TEMPERATURE = 0
IS_STREAM = False
MAX_TOKENS = -1