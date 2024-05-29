import os

LLM_URL = os.getenv('LLM_URL')
PROMPT_TEMPLATE = """
You are a helpful, respectful and honest assistant.
Always answer a question based on the INSTRUCTION.

INSTRUCTION: 
Answer the QUESTION using the CONTEXT provided below. If the question can't be answered, use your knowledge to answer the question.

CONTEXT:
{context}

HISTORY:
{history}

QUESTION:
{question}

"""
MODEL = "gpt-4"
TEMPERATURE = 0
IS_STREAM = False
MAX_TOKENS = -1