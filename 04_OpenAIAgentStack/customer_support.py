"""
Complete Project - Customer Support Agent System

This brings together EVERYTHING from the course:
- Multiple agents with handoffs
- Custom function tools
- Input guardrails
- Hosted tools - WebSearchTool
- Structured output with Pydantic

Architecture:
User -> Triage Agent -> Order Status Agent (with lookup_order tool)
                    -> Refund Agent (with process_refund tool)
                    -> FAQ Agent (with web search)
"""

from dotenv import load_dotenv
import warnings
import asyncio

from pydantic import BaseModel

from agents import (
    Agent,
    Runner,
    function_tool,
    GuardrailFunctionOutput,
    input_guardrail,
    InputGuardrailTripwireTriggered,
    WebSearchTool,
)


# SETUP

warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

MODEL = "gpt-4.1-mini"


# PART 1: DEFINE CUSTOM TOOLS

# Simulated database
ORDERS_DB = {
    "ORD-001": {
        "item": "Wireless Headphones",
        "status": "Shipped",
        "eta": "Aug 28",
    },
    "ORD-002": {
        "item": "Python Programming Book",
        "status": "Delivered",
        "eta": "Aug 18",
    },
    "ORD-003": {
        "item": "USB-C Cable 3-pack",
        "status": "Processing",
        "eta": "Sept 4",
    },
}


@function_tool
def lookup_order(order_id: str) -> str:
    """Look up the status of a customer order by order ID (e.g., ORD-001)."""

    order = ORDERS_DB.get(order_id.upper())

    if order:
        return (
            f"Order: {order_id.upper()}\n"
            f"  Item: {order['item']}\n"
            f"  Status: {order['status']}\n"
            f"  Estimated Arrival: {order['eta']}"
        )

    return (
        f"Order {order_id.upper()} not found. "
        "Please check the order ID and try again."
    )


@function_tool
def process_refund(order_id: str, reason: str) -> str:
    """Process a refund request for a given order ID with a reason."""

    order = ORDERS_DB.get(order_id.upper())

    if not order:
        return (
            f"Cannot process refund: "
            f"Order {order_id.upper()} not found."
        )

    if order["status"] == "Processing":
        return (
            f"Refund for {order_id.upper()} cannot be processed. "
            "The order hasn't shipped yet. It can be cancelled instead."
        )

    return (
        f"Refund Initiated for Order {order_id.upper()}\n"
        f"  Item: {order['item']}\n"
        f"  Reason: {reason}\n"
        "  Refund amount will be credited within 5-7 business days."
    )


# PART 2: DEFINE GUARDRAIL

class SupportCheck(BaseModel):
    is_support_question: bool
    reasoning: str


guardrail_checker = Agent(
    name="Support Topic Checker",
    instructions="""
    Determine if the user's message is a customer support question.

    Valid topics:
    - Order status
    - Refunds
    - Returns
    - Product questions
    - Shipping
    - FAQs

    Invalid topics:
    - Personal advice
    - Jokes
    - Coding help
    - Unrelated conversations

    Return is_support_question=True ONLY for customer support topics.
    """,
    output_type=SupportCheck,
    model=MODEL,
)


@input_guardrail(run_in_parallel=False)
async def support_only(ctx, agent, input):
    """Only allow customer support questions."""

    result = await Runner.run(
        guardrail_checker,
        input,
        context=ctx.context,
    )

    final = result.final_output_as(SupportCheck)

    return GuardrailFunctionOutput(
        output_info={
            "reasoning": final.reasoning
        },
        tripwire_triggered=not final.is_support_question,
    )


# PART 3: DEFINE SPECIALIST AGENTS

order_agent = Agent(
    name="Order_Status_Agent",
    handoff_description=(
        "Handles questions about order status, shipping, and delivery."
    ),
    instructions="""
    You help customers check their order status.

    Use the lookup_order tool to find order information.

    If the customer doesn't provide an order ID, ask for it.

    Be friendly and professional.
    """,
    tools=[lookup_order],
    model=MODEL,
)


refund_agent = Agent(
    name="Refund_Agent",
    handoff_description=(
        "Handles refund requests, returns, and cancellations."
    ),
    instructions="""
    You help customers with refunds and returns.

    Use the process_refund tool to initiate refunds.

    Always ask for the order ID and reason before processing.

    Be empathetic and helpful.
    """,
    tools=[process_refund],
    model=MODEL,
)


faq_agent = Agent(
    name="FAQ_Agent",
    handoff_description=(
        "Handles general product questions and frequently asked questions."
    ),
    instructions="""
    You answer general customer questions and FAQs.

    Use web search when you need current information.

    Common topics:
    - Shipping policies
    - Return windows
    - Product details

    Be helpful and concise.
    """,
    tools=[WebSearchTool()],
    model=MODEL,
)


# PART 4: DEFINE TRIAGE AGENT

triage_agent = Agent(
    name="Customer Support Agent",
    instructions="""
    You are a front-line customer support agent.

    Your job is to understand the customer's issue
    and route them to the right specialist.

    - Order status, shipping, delivery questions
      -> Order Status Agent

    - Refund requests, returns, cancellations
      -> Refund Agent

    - General questions, product information, FAQs
      -> FAQ Agent

    Be warm, professional, and route quickly.
    """,
    handoffs=[
        order_agent,
        refund_agent,
        faq_agent,
    ],
    input_guardrails=[support_only],
    model=MODEL,
)


# PART 5: RUN THE SYSTEM

async def handle_customer(message: str):
    """Process the customer message through the support system."""

    print(f"\nCustomer: {message}")

    try:
        result = await Runner.run(
            triage_agent,
            message,
        )

        print(
            f"{result.last_agent.name}: "
            f"{result.final_output}"
        )

    except InputGuardrailTripwireTriggered:
        # Expected behavior for off-topic questions
        print(
            "Blocked: This doesn't appear to be "
            "a customer support question."
        )

    except Exception as e:
        # Unexpected errors should NOT be reported as guardrail blocks
        print("Error: Something went wrong while processing the request.")
        print(f"Details: {type(e).__name__}: {e}")

    print("-" * 70)
    print()


# PART 6: TEST THE SYSTEM

async def main():

    print("-" * 70)
    print("CUSTOMER SUPPORT AGENT SYSTEM - SIMULATION")
    print("-" * 70)

    # TEST 1:
    # Order Status
    # -> Triage Agent
    # -> Order Status Agent
    # -> lookup_order tool

    await handle_customer(
        "Where is my Order ORD-001?"
    )

    # TEST 2:
    # Refund Request
    # -> Triage Agent
    # -> Refund Agent
    # -> process_refund tool

    await handle_customer(
        "I want a refund for Order ORD-001. "
        "The headphones arrived damaged."
    )

    # TEST 3:
    # General FAQ
    # -> Triage Agent
    # -> FAQ Agent
    # -> WebSearchTool

    await handle_customer(
        "What is Amazon's return policy in India?"
    )

    # TEST 4:
    # Off-topic
    # -> Input Guardrail
    # -> Blocked

    await handle_customer(
        "Give Java code to print the first 10 natural numbers."
    )


# ENTRY POINT

if __name__ == "__main__":
    asyncio.run(main())

