from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4.1-mini"

# Step 1: Specialist agents

math_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist for math questions, equations, and calculations.",
    instructions="""
    You are an expert math tutor.
    Explain math step by step with worked examples.
    Use simple language that beginners can understand.
    """,
    model=MODEL,
)

history_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist for history questions and historical events.",
    instructions="""
    You are an expert history tutor.
    Answer history questions with key facts and context.
    Include interesting stories to make history come alive.
    """,
    model=MODEL,
)

# Step 2: Triage agent

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are a helpful homework assistant.

    Your job is to route each question to the right specialist tutor.

    - Math questions -> Math Tutor
    - History questions -> History Tutor
    - Science questions -> answer yourself

    If the question doesn't fit any category,
    do your best to answer it yourself.
    """,
    handoffs=[math_agent, history_agent],
    model=MODEL,
)

questions = [
    "What is 15% of 240?",
    "Who built the Great Wall of China and why?",
    "How does photosynthesis work?",
]

for q in questions:
    print(f"\nQuestion: {q}")

    result = Runner.run_sync(triage_agent, q)

    print(f"Answer:\n{result.final_output}")
    print(f"Answered by: {result.last_agent.name}")