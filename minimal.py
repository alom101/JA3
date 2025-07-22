import requests
import json
from pprint import pprint
from tools import tools, functions

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"



messages = []


def append_message(message, role="user"):
    messages.append({
        "role": role,
        "content": message
    })


def request_llm_response():
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False
    }
    with requests.post(OLLAMA_API_URL, json=payload) as response:
        response.raise_for_status()
    messages.append(response.json()["message"])

    if("tool_calls" in response.json()["message"]):
        for tool in response.json()["message"]['tool_calls']:
            func = functions[tool["function"]["name"]]
            args = tool["function"]["arguments"]
            ret = func(**args)
            append_message(json.dumps(ret), "tool")
        request_llm_response()


def print_tools(tool_calls):
    for tool in tool_calls:
        tool = tool['function']
        print(f"{tool['name']}({tool['arguments']})")


def print_chat(message):
    if (type(message) is list):
        for m in message:
            print_chat(m)
        return

    role = message['role']
    text = message['content']
    tool_calls = None
    if ('tool_calls' in message):
        tool_calls = message['tool_calls']
    thoght = None
    if ("</think>" in text and "<think>" in text):
        thoght, text = text.split("</think>")
        thoght = thoght.removeprefix("<think>").strip()
        text = text.strip()

    print('-'*20)
    print(f'>>Role: {role.upper()}')
    if (thoght):
        print(f">>Thinking:\n{thoght}")
    print(f'>>Response:\n{text}\n\n')
    if (tool_calls):
        print(f">>Tool calls:\n")
        print_tools(tool_calls)



append_message("You are a helpful assistant. Do not invent anything nor give probable answers. Just ask for more info. Also if you need the response of some tool, wait the response, dont assume anything. When tools are run, the assistant have another turn to process the data, it can even run other tools again.", "system")


# append_message("Whats 11+33?")
# request_llm_response()
# append_message("Whats 11-10?")
# request_llm_response()

append_message("What is 10 + 42 - 44? Use tools to calculate each step")
request_llm_response()


# append_message("Write a small python numpy example. Use the current temperature.")
# request_llm_response()
# append_message("We are at São Paulo. Use the default unit.")
# request_llm_response()
# append_message("Current temperature at São Paulo is 17ºC", "tool")
# request_llm_response()


print("FINAL\n")
print_chat(messages)
