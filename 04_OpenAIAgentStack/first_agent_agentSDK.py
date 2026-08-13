from agents import Agent, Runner
from dotenv import load_dotenv
load_dotenv()
# Step 1: Define an Agent
# An Agent needs:
# - name: a label for identification and tracing
# - instructions: the system prompt that defines behavior
# - model name: OpenAI Models

agent = Agent(
    name="Quick Helper",
    instructions="Give very brief, one-sentence answers.",
    model="gpt-4.1-mini", # Faster, cheaper model
)


# Step 2: Run the Agent
# Runner.run_sync() is the synchronous way to execute an agent.
# (There's also an async version: await Runner.run())

result = Runner.run_sync(agent, "When did humans land on the moon?")

print(result.final_output)
# output: Humans first landed on the Moon on July 20, 1969.