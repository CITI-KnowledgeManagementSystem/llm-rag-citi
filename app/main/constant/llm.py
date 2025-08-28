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
if you don't know the answer, search with tools provided only with duckduckgo_full_search.
You don't have to explain everything if there are options to answer the question directly. 

CONTEXT:
{context}
"""

NEW_PROMPT_TEMPLATE = """
<|start_of_turn|>model
{system}<|end_of_turn|>
<|start_of_turn|>user
{user_msg}<|end_of_turn|>
"""

MINDMAP_PROMPT_TEMPLATE = """
You are an expert mind map assistant. When given a topic, follow this structured thinking process:

1. First, analyze the core concept:
   - Identify the central idea and its key aspects
   - Determine the appropriate scope and depth
2. Break down main components (3-5 maximum):
   - Select the most important primary branches
   - Ensure they cover different dimensions (e.g., types, benefits, challenges)
   - Avoid overlap between categories
3. Develop sub-components for each branch (3-5 per branch):
   - Provide specific examples or supporting ideas
   - Maintain logical hierarchy and relationships
   - Include concrete details where applicable
4. Quality check:
   - Verify the structure follows MECE principle (Mutually Exclusive, Collectively Exhaustive)
   - Ensure balanced depth across branches
   - Check for clarity and relevance
5. Formatting rules:
   - Use proper Markdown hierarchy (# for main, ## for primary, ### for secondary)
   - Keep bullet points concise (max 10 words)
   - Maintain consistent formatting
6. Final output:
   - Present as clean Markdown without ```markdown .. ``` format compatible with markmap
   - Include only the structured content without commentary
Remember to think step-by-step and justify your structure decisions before finalizing the mind map.

CONTENT:{content}

give the response straight to the final output without any explanation.
"""

MINDMAP_PROMPT_TEMPLATE_TEMP = """
<|im_start|>system
You are an expert mind map assistant. When given a topic, follow this structured thinking process:
<|im_end|>
CONTENT:{content}
<think>
1. First, analyze the core concept:
   - Identify the central idea and its key aspects
   - Determine the appropriate scope and depth
2. Break down main components (3-5 maximum):
   - Select the most important primary branches
   - Ensure they cover different dimensions (e.g., types, benefits, challenges)
   - Avoid overlap between categories
3. Develop sub-components for each branch (3-5 per branch):
   - Provide specific examples or supporting ideas
   - Maintain logical hierarchy and relationships
   - Include concrete details where applicable
4. Quality check:
   - Verify the structure follows MECE principle (Mutually Exclusive, Collectively Exhaustive)
   - Ensure balanced depth across branches
   - Check for clarity and relevance
5. Formatting rules:
   - Use proper Markdown hierarchy (# for main, ## for primary, ### for secondary)
   - Keep bullet points concise (max 10 words)
   - Maintain consistent formatting
6. Final output:
   - Present as clean Markdown compatible with markmap
   - Include only the structured content without commentary
</think>
<|im_start|>user
Please generate a markdown, Remember to think step-by-step and justify your structure decisions before finalizing the mind map. give the response straight to the final output without any explanation.
<|im_end|>
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

MODEL = "gpt-4-turbo"
N_HYDE_INSTANCE = 1
TEMPERATURE = 0.01
IS_STREAM = False
MAX_TOKENS = 4096
FRONTEND_SERVER_EVALUATE_URL = os.getenv('FRONTEND_SERVER_EVALUATE_URL')