

tools = []
functions = {
}

# def llm_tool(func):
#
#     def 
#
#
# @llm_tool
def my_sum(a, b):
    """ Sums two numbers"""
    return a-b

functions["sum"] = my_sum
tools.append(
    {
            "type": "function",
            "function": {
                "name": "sum",
                "description": my_sum.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "a number"
                        },
                        "b": {
                            "type": "number",
                            "description": "another number"
                        }
                    },
                    "required": ["a", "b"]
                }
            }
        }
)



def my_sub(a, b):
    """ Subtract two numbers"""
    return a-b

functions["sub"] = my_sub
tools.append(
    {
            "type": "function",
            "function": {
                "name": "sub",
                "description": my_sub.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "a number"
                        },
                        "b": {
                            "type": "number",
                            "description": "another number"
                        }
                        },
                    "required": ["a", "b"]
                }
            }
        }
)
