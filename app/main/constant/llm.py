import os

LLM_URL = os.getenv('LLM_URL')
HYDE_LLM_URL = os.getenv('HYDE_LLM_URL')
HYDE_PROMPT_TEMPLATE = """
You are a helpful AI assistant. Please give context to the user's question based on your knowledge.
The response should be an explanation of the user's question and then followed by the hypothetical answers to the question.
Another criteria is that the response should not specify which time period the information is from. 
Question: {question}
"""
PROMPT_TEMPLATE = """
INSTRUCTION: 
You are a helpful, respectful and honest assistant.
Answer the QUESTION with the help by the CONTEXT provided. If the question can't be answered, use your knowledge to answer the question.
You don't have to explain everything if there are options to answer the question directly. 

CONTEXT:
{context}
"""


PODCAST_SCRIPT_TEMPLATE = """
You are a podcast script writer. Create an engaging conversational podcast script between two hosts discussing the provided content. 

INSTRUCTIONS:
- Create a natural, engaging conversation between Host A and Host B
- Host A should be more analytical and fact-focused
- Host B should be more conversational and ask clarifying questions
- Include smooth transitions between topics
- Make it sound like a real conversation with natural interruptions, agreements, and follow-up questions
- Keep each speaking segment between 1-3 sentences
- Use the format: "HOST_A: [text]" and "HOST_B: [text]"
- Start with a brief introduction about the topic
- End with a summary or key takeaways

CONTENT TO DISCUSS:
{content}

QUESTION/TOPIC: {question}

Generate a podcast script that covers the main points from the content in a conversational format:
"""

# MODEL = "gpt-4-turbo"
MODEL = "gpt-4o"
N_HYDE_INSTANCE = 1
TEMPERATURE = 0.01
IS_STREAM = False
MAX_TOKENS = 1000