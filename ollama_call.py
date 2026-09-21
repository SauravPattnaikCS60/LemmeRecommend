from ollama import chat
from ollama import ChatResponse


def call_ollama_qwen(prompt):
    response: ChatResponse = chat(model='qwen3.5:9b', messages=[
    {
        'role': 'user',
        'content': prompt,
    }
    ],think=False)
    return response['message']['content']