# MCP + LangChain Agent - Before & After Comparison

# This is the SAME agent as first_agent.py, but instead of
# defining tools locally with @tool, it discovers them from
# an MCP server at runtime.

# THE KEY DIFFERENCE:

# BEFORE (first_agent.py):
    # Tools are hardcoded in the agent's code.
    # Every agent must redefine the same tools.
    # Changing a tool = changing every agent.

# AFTER (this file):
    # Tools live on an MCP server.
    # Any agent can discover & use them.
    # Changing a tool = update one server.
    # Tools are reusable across Claude, ChatGPT,
    # Cursor, VS Code, and your own agents.

# Prerequisites:
# pip install langchain langchain-openai langgraph
# pip install langchain-mcp-adapters mcp python-dotenv

# Setup:
# Create a .env file with: OPENAI_API_KEY=sk-your-key-here

# Make sure mcp_math_server.py is in the same directory.

# Usage:
# python first_agent_with_mcp.py
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# STEP1- Initialize the model

    # SAME AS BEFORE - the model doesn't change.
    # MCP only changes WHERE tools come from,
    # not how the LLM reasons about them.
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

# Change this line:
# model = init_chat_model("openai:gpt-4o-mini")

# To this:
# model = init_chat_model("openai:gpt-4o-mini").bind(parallel_tool_calls=False)
model = ChatOpenAI(model='gpt-5.5', parallel_tool_calls=False)


# STEP2 - Define Tools
    # before mcp tools were right here with @tool decorators
    # Hardcodeed,tightly coupled to this one agent file

    # With MCP tools are discovered from mcp server at runtime
    # no @tool decorators . no local function definition


from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    """
     Main async function - MCP connections are async because
     they involve I/O (spawning process, network calls).
    """

    # Connect to the MCP Server

    # This is the NEW part. Instead of defining tools locally,
    # we point to an MCP server and let the adapter discover
    # all available tools automatically.

    # The MultiServerMCPClient can connect to MULTIPLE servers
    # at once - imagine combining a math server + a GitHub
    # server + a database server, all in one agent!

    # Get the absolute path to the MCP server script
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    server_path = os.path.join(curr_dir,"mcp_math_server.py")

    client = MultiServerMCPClient(
        {
            "math":{
                # the mcp server to connect to
                "command":"python",
                "args":[server_path],
                "transport":"stdio" # local process (stdin/stdout)

            },
            # if want more tools just add more servers
            # no code changes to agent logic is needed
            # "github": {
            #     "command": "npx",
            #     "args": ["-y", "@modelcontextprotocol/server-github"],
            #     "transport": "stdio",
            #     "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")},
            # },
            # "weather": {
            # "url": "http://localhost:8000/mcp",
            # "transport": "http", # Remote server
            # },
        }
    )

    # DISCOVER TOOLS FROM MCP SERVER

    # this is where magic happens

    # the client connects to server, performs the MCP handshake, and auto discovers all available tools.
    #each mcp tool is converted into Langchain tool

    tools = await client.get_tools();

    print("-" * 60)
    print("MCP Agent- Tools Discovered from MCP server")
    print("-" * 60)

    print(f"\n Found {len(tools)} tools from MCP server: \n")
    for t in tools:
        print(f"{t.name} : {t.description[:60]}...")
    print()


    # STEP3- Create Agent

    # SAME AS BEFORE - the agent creation is identical!
    # The agent doesn't know or care that tools came from MCP.
    # It just sees LangChain tools and uses them normally.

    # IMPORTANT: parallel_tool_calls=False

    # By default, newer OpenAI models (GPT-40, GPT-4o-mini)
    # try to call multiple tools at the same time (in parallel)
    # to be faster. This causes WRONG ANSWERS for sequential
    # math like "15 x 8, then + 3" because the LLM calls
    # multiply(15,8) AND divide(15,3) simuItaneously instead
    # of waiting for the multiply result first.

    # Setting parallel_tool_calls=False forces the LLM to
    # call tools one at a time, in the correct order.

    agent  = create_agent(
        model,
        tools=tools
    )

    # STEP4 - RUN AGENT

    async def run_agent(question: str):
        """ run the agent and print the xecution trace"""
        print(f"User Question: {question}")

        print("-" *60)

        result = await agent.ainvoke({
            "messages":[("user", question)]
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
    # await run_agent("What is 42 + 58")
    
    # 2. Medium Complexity - multiple steps
    #await run_agent("What is 15 multiplied by 8, then divide by 3?")
    
    # 3. Complex Reasoning- Planning required
    # agent must:
        # step1: calculate area
        # step2: calculate square root
        
    # await run_agent(
    #     "I have a rectangle with width 12 and height 7."
    #     "What is its area, and what is the square root of that area?"
    # )
    
    # 4. Edge cases
    await run_agent("What is 100 divided by 0")
        
        
if __name__ == "__main__":
    asyncio.run(main())
