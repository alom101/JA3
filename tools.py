
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
