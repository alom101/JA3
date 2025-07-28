import requests

from message import Message


# MODEL RELATED CODE 
# To be splited into Model and Actor

class Model:
    def __init__(self,
                 model_name="llama3.1:8b",
                 ollama_api="http://localhost:11434/api/chat"
                 ):
        self.model = model_name
        self.api = ollama_api
        self.messages = []
        self.tools = []

    def request_assistant_message(self):
        payload = {
            "model": self.model,
            "messages": [msg.encode() for msg in self.messages],
            "tools": [tool.encode() for tool in self.tools],
            "stream": False
        }

        with requests.post(self.api, json=payload) as response:
            response.raise_for_status()
            last_message = Message(response.json())
        self.messages.append(last_message)

        if (last_message.has_tool_call()): # Maybe some BUG here, the tool is called even when not needed
            for tool_call in last_message.tool_calls:
                tool = self.get_tool_by_name(tool_call.name)
                response = Message.as_tool(tool.run(**tool_call.arguments), tool)
                self.messages.append(response)
                self.request_assistant_message()

    def add_tool(self, tool):
        self.tools.append(tool)

    def add_message(self, message):
        self.messages.append(message)

    def get_tool_by_name(self, tool_name):
        for tool in self.tools:
            if (tool.name == tool_name):
                return tool

    def chat(self):
        while True:
            try:
                msg = input(">> ")
                print("\r", end="")
                self.messages.append(Message.as_user(msg))
                self.request_assistant_message()
            except KeyboardInterrupt:
                return





if (__name__ == "__main__"):

    model = Model(model_name="llama3.1:8b")
    # model = Model(model_name="qwen3:1.7b")
    # model = Model(model_name="qwen3:4b")

    from basic_tools import CalculatorTool
    model.add_tool(CalculatorTool())

    model.add_message(Message.as_system("You are a helpful assistant. Your job is to answer the user. You have some tools on your disposal but you should use them for their intended porpose, also do not call them if not needed. Just responding in text to the user is a valid answer."))
    # model.add_message(Message.as_user("I have 111 coins, I invested them and received 1.6 times the amount back. How many coins I have now?"))
    # model.request_assistant_message()

    model.chat()

    print("\n\n__MESSAGE_DEBUG__")
    for msg in model.messages:
        msg.display(raw=True)
