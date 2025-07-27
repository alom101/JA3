import requests
from datetime import datetime
from enum import Enum


class Model:
    def __init__(self,
                 model_name="gemma3:1b",
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

        if (last_message.has_tool_call()):
            for tool_call in last_message.tool_calls:
                tool = self.get_tool_by_name(tool_call.name)
                response = Message.as_tool(tool.run(**tool_call.arguments), tool)
                self.messages.append(response)
                self.request_assistant_message()

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


class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSITANT = "assistant"
    TOOL = "tool"


class Message:
    def __init__(self, raw_message):
        if ("message" in raw_message):
            raw_message = raw_message['message']
        self.raw_message = raw_message
        self.full_message = self.raw_message["content"]  # with thinking!
        if ("</think>" in self.full_message):
            self.thought, self.message = self.full_message.split("</think>")
            self.thought.removeprefix("<think>")
        else:
            self.thought = ""
            self.message = self.full_message
        self.thought.strip()
        self.message.strip()
        self.role = Role(self.raw_message["role"])
        self.datetime = datetime.now()
        self.tool_calls = []
        if ("tool_calls" in self.raw_message):
            for tool_call in self.raw_message["tool_calls"]:
                self.tool_calls.append(ToolCall(tool_call))

        self.display(False)

    @classmethod
    def decode(cls, raw_message):
        return cls(raw_message)

    @classmethod
    def as_user(cls, message):
        return cls({
            "role": "user",
            "content": str(message)
        })

    @classmethod
    def as_tool(cls, message, tool):
        return cls({
            "role": "tool",
            "content": str(message),
            "tool_called": tool.name
        })

    @classmethod
    def as_system(cls, message):
        return cls({
            "role": "system",
            "content": str(message)
        })

    @classmethod
    def as_assistant(cls, message):
        return cls({
            "role": "assistant",
            "content": str(message)
        })

    def encode(self, remove_thought=True):
        msg = self.full_message
        if (remove_thought):
            msg = self.message

        return {
            "role": self.role.value,
            "content": msg
        }

    def has_tool_call(self):
        return "tool_calls" in self.raw_message

    def __repr__(self):
        role = self.role.value
        msg = self.full_message[:40].replace("\n", "<new_line>")
        return f"Message(role={role}, msg={msg})"

    def display(self, raw=False):
        """ To be used to display as chat """
        if (raw):
            __import__('pprint').pprint(self.raw_message)
        elif (self.has_tool_call()):
            print(f'{self.role.name}:\n\t{self.full_message}\n\tTools called:{[self.tool_calls]}')
        else:
            print(f'{self.role.name}:\n\t{self.full_message}\n')


class Tool:
    def __init__(self, name, description, properties):
        self.name = name
        self.description = description
        self.properties = properties

    def encode(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {property.name: property.encode()
                                   for property in self.properties},
                    "required": [property.name
                                 for property in self.properties
                                 if property.required]
                }
            }
        }

    def run(self, query, *args, **kwargs):
        raise NotImplementedError


class ToolProperty:
    def __init__(self, name, _type, description, required, enum=[]):
        self.name = name
        self.type = _type
        self.description = description
        self.required = required
        self.enum = enum

    def encode(self):
        resp = {
            "type": self.type,
            "description": self.description
        }
        if (self.enum):
            resp["enum"] = self.enum
        return resp


class ToolCall:
    ''' Representation of the tool_call from the llm response '''

    def __init__(self, raw_tool_call):
        self.raw_tool_call = raw_tool_call
        if ("function" in raw_tool_call):
            self.raw_tool_call = self.raw_tool_call["function"]
        self.arguments = self.raw_tool_call["arguments"]
        self.name = self.raw_tool_call["name"]

    def __repr__(self):
        return f"{self.name}({list(self.arguments.values())})"


# Tool implementations

class CalculatorTool(Tool):
    def __init__(self):
        operation = ToolProperty(
            name="operation",
            _type="text",
            description="The operation to perform ('add', 'subtract', 'multiply', 'divide')",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        )
        num1 = ToolProperty("num1", "float", "First number", True)
        num2 = ToolProperty("num2", "float", "Second number", True)
        super().__init__("calculator", "Prerforms a basic arithmetic operation between two numbers", [operation, num1, num2])

    def run(self, operation, num1, num2, *args, **kwargs):
        num1 = float(num1)
        num2 = float(num2)
        if operation == 'add':
            return num1 + num2
        elif operation == 'subtract':
            return num1 - num2
        elif operation == 'multiply':
            return num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                raise ValueError("Cannot divide by zero.")
            return num1 / num2
        else:
            return "Invalid operation. Choose from 'add', 'subtract', 'multiply', 'divide'."




if (__name__ == "__main__"):
    # path_prop = ToolProperty("path", "text", "A path for the execution of the command. Relative to the current working directory", False)
    # ls = Tool("ls", "List the a directory", [path_prop])
    #
    # cmd_prop = ToolProperty("terminal_command", "text", "Arbitrary terminal command", True)
    # cmd = Tool("terminal_command", "Run a command on terminal(Bash)", [cmd_prop])

    # query = ToolProperty("query", "text", "query for the search", True)
    # google_query = Tool("google_query", "Query a string on google. Returns the HTML of the page", [query])

    model = Model(model_name="llama3.1:8b")
    # model = Model(model_name="qwen3:1.7b")
    # model = Model(model_name="qwen3:8b")
    # model = Model()

    # model.tools.append(ls)
    # model.tools.append(cmd)
    # model.tools.append(google_query)
    model.tools.append(CalculatorTool())


    model.messages.append(Message.as_system("You are a helpful assistant"))
    model.messages.append(Message.as_user("I have 111 coins, I invested them and received 1.6 times the amount back. How many coins I have now?"))
    model.request_assistant_message()

    # model.messages.append(Message.as_user("How many files there are on the current directory?"))
    # model.request_assistant_message()

    # model.messages.append(Message.as_system("You are an helpful assistant with senior knwoledge in python an ollama"))
    # model.messages.append(Message.as_user("Explain how the ollama api works"))
    # model.request_assistant_message()
    # model.messages.append(Message.as_user("Write me a example code for ollama api"))
    # model.request_assistant_message()
    # model.messages.append(Message.as_user("Give me a thoughtfull analisys of the code and give suggestions to make it better"))
    # model.request_assistant_message()
    # model.messages.append(Message.as_user("Now use the tool SAVE_TO_FILE{[your_file_here]} to write the code to a file ollama.py"))
    # model.request_assistant_message()

    # for msg in model.messages:
    #     msg.display(raw=False)

    model.chat()
