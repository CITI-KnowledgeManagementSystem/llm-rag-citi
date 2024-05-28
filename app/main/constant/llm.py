import os

LLM_URL = os.getenv('LLM_URL')
PROMPT_TEMPLATE = """
You are a helpful, respectful and honest assistant.
Always answer a question based on the INSTRUCTION.

INSTRUCTION: 
Answer the QUESTION using the CONTEXT provided below. Prioritize answering the QUESTION based on the provided CONTEXT. If the QUESTION can't be answered using the CONTEXT, tell that in your answer and provide a factual answer. Use the HISTORY also to answer the QUESTION.

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