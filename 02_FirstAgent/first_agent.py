# STEP 0 : Load environment variables
from dotenv import load_dotenv
load_dotenv() 

# STEP 1: Initialize the Model (the "brain")
# this is llm that will:
    #understand the qn
    # decide which tool to use
    # generate the final answer
from langchain.chat_models import init_chat_model

# gpt 5.5 is latest 
model = init_chat_model("openai:gpt-5.5")

# STEP2 : Define Your Tools (the "Hands")

# each tool must have:
    # clear name
    # Descriptive docstring (very important)
    # Type hints (so llmm knows expected inputs)

from langchain_core.tools import tool
import math

@tool
def add(a: float, b: float) -> float:
    """
    Add two numbers together.
    The agent will use this when it detects an addition problem
    """

    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers together.
    Used for multiplication tasks
    """
    return a * b;

@tool
def divide(a: float , b: float) -> str:
    """
    Divide the first number by the second.
    Include error handling for divide by zero.
    """

    if b == 0:
        return "Error: cannot divide by zero."
    return str(a / b)

@tool
def square_root(number: float) -> str:
    """
    Calculate the square root of a number.
    Include error handling for negative input.
    """

    if number < 0:
        return "Error: cannot find square root of negative nuber."
    
    return str(math.sqrt(number))


# combine tools into a list
tools = [add,multiply,divide,square_root]

# check tools
print("AVAILABLE TOOLS")

for t in tools:
    print(f"{t.name}: {t.description}")


#STEP3: Create the agent

# create_agent automatically builds ReAct loop:
    # 1. Reason- LLM decides what to do
    # 2. Act- calls a tool (if needed)
    # 3. Observe- gets the result
    # 4. Repeat until done
# we dont hqve to manually write th eloop - the framework does it.

from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=tools,
)

# STEP4: Run the Agent

def run_agent(question: str):
    """
    Run the function and print a clean, beginner-friendly execution trace.
    """

    print("-" *40)
    print(f"Question: {question}")
    

    result = agent.invoke({
        "messages":[("user",question)]
    })

    print("Agent execution trace: ")

    step = 1
    for msg in result["messages"]:

        # human msg - Originl user question
        if msg.type=="human":
            print(f"{step}. User asked: ")
            print(msg.content)
            step += 1
        # AI message with tool call- Agent decided t use tool
        elif msg.type=='ai' and getattr(msg, "tool_calls",None):
            for tool_call in msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(f"{step}. Agent Decision:")
                print(f"I need to use tool: {tool_name}")
                print(f"Tool input: {tool_args}")
                step += 1

        # Tool message - result returned by tool
        elif msg.type=='tool':
            print(f"{step}. Tool observation:")
            print(f"Tool Returned: {msg.content}")
            step+=1
        # final AI msg- final response to user
        elif msg.type == 'ai':
            print(f"{step}. Final Answer: ")
            print(msg.content)
            step += 1
    print("-" *40)

# TEST_CASES

# 1. Simple case- single tool call
# run_agent("What is 42 + 58")

# 2. Medium Complexity - multiple steps
# run_agent("What is 15 multiplied by 8, then divide by 3?")

# 3. Complex Reasoning- Planning required
# agent must:
    # step1: calculate area
    # step2: calculate square root
    
# run_agent(
#     "I have a rectangle with width 12 and height 7."
#     "What is its area, and what is the square root of that area?"
# )

# 4. Edge cases
run_agent("What is 100 divided by 0")


