from datetime import datetime
from enum import Enum

from tools import ToolCall

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

        self.display(False)  # TODO: find a better way do display all messages on receive

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

    def is_system_prompt(self):
        return self.role == Role.SYSTEM

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
