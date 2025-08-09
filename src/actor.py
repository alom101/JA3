from src.history import History
from src.message import Message


class Actor:
    def __init__(self, model, history=None, tools=[]):
        self.model = model
        self.history = history if history else History()
        self.history.set_owner(self)
        self.tools = tools

    def add_system_prompt(self, message):
        self.history.add(message)

    def __call__(self, message: str):
        _from = message.role
        self.history.add(message, _from)
        response = self.model(self.history.messages(), self.tools)
        self.history.add(response, _from=self)

        if (response.has_tool_call()):
            for tool_call in response.tool_calls:
                tool = self.get_tool_by_name(tool_call.name)
                tool_response = Message.as_tool(tool.run(**tool_call.arguments), tool)
                self.history.add(tool_response, _from=tool)
            response = self.model(self.history.messages(), self.tools)
            self.history.add(response, _from=self)

        return response

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
