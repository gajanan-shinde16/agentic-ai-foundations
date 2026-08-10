from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool


# Initialize the model
model = init_chat_model("openai:gpt-4o")


# Define tools
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together. Use for multiplication operations."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide the first number by the second. Returns error if dividing by zero.""" #docstring
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b


# Create agent
agent = create_agent(model, [multiply, divide])


# Run agent
result = agent.invoke({
    "messages": [
        ("user", "What is 15 multiplied by 8, then divided by 3?")
    ]
})

print(result)
print(result["messages"][-1].content)