import requests
from message import Message

class Model:
    def __init__(self,
                 model_name="llama3.1:8b",
                 ollama_api="http://localhost:11434/api/chat"
                 ):
        self.model = model_name
        self.api = ollama_api

    def __call__(self, messages, tools):
        __import__('pprint').pprint(messages)
        payload = {
            "model": self.model,
            "messages": [msg.encode() for msg in messages],
            "tools": [tool.encode() for tool in tools],
            "stream": False
        }

        with requests.post(self.api, json=payload) as response:
            response.raise_for_status()
        return Message(response.json())


