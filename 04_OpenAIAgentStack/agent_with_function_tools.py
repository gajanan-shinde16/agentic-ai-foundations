from agents import Agent,function_tool,Runner
from dotenv import load_dotenv
import math

load_dotenv()

@function_tool
def add(a: float, b: float) -> float:
    "tool used for two number addition"

    return a+b;

@function_tool
def multiply(a: float, b: float) -> float:
    "tool used for two number multiplication"

    return a*b;



@function_tool
def divide(a: float, b: float) -> float:
    "tool used to divide first number by second number"\

    if b==0:
        return "Error: cannot divide by 0"

    return str(a/b);

@function_tool
def square_root(a: float) -> str:
    "tool use for two number addition"

    if a<0:
        return "Error: cannot find root of negative numbers"
    
    return str(math.sqrt(a));

tools = [add,multiply,divide,square_root]


agent = Agent(
    name='Math Assistant',
    instructions="You are a math assistant, use tools to answer questions",
    tools=tools,
    model='gpt-4.1-mini'
)

def run_agent(qn: str):
    "Run the agent and print the result"

    print(f"User QN: {qn}")
    response = Runner.run_sync(agent,qn)
    print(f"Response: {response.final_output}")


# case1

run_agent("what is 3 + 4")
print("\n\n")
run_agent("what is 3 multiplied by 10 , and then divide result by 5")

'''
OUTPUT: 
User QN: what is 3 + 4
Response: 3 + 4 is 7.



User QN: what is 3 multiplied by 10 , and then divide result by 5
Response: 3 multiplied by 10 is 30, and then dividing the result by 5 gives 6.
'''