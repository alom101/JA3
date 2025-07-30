from actor import Actor
from model import Model
from message import Message
from history import History
from basic_tools import CalculatorTool

model = Model(model_name="llama3.1:8b")
# model = Model(model_name="qwen3:1.7b")
# model = Model(model_name="qwen3:4b")

calc = CalculatorTool()
history = History()

actor = Actor(model, history, tools=[calc])

actor.add_system_prompt(Message.as_system("You are a helpful assistant. Your job is to answer the user. You have some tools on your disposal but you should use them for their intended porpose, also do not call them if not needed. Just responding in text to the user is a valid answer."))
actor(Message.as_user("I have 111 coins, I invested them and received 1.6 times the amount back. How many coins I have now?"))

# model.chat()

print("\n\n__MESSAGE_DEBUG__")
for msg in history._messages:
    msg.display(raw=True)
