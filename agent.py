import boto3
from strands import Agent, AgentSkills
from strands.models import BedrockModel
from customer_service_tools import (
    lookup_customer,
    get_order_history,
    process_refund,
)
from hooks import ToolCallLimiter
from steering_handlers import RefundWorkflowHandler
from strands.session import SnapshotSessionManager
from strands.storage import LocalFileStorage
import re

aws_session = boto3.Session(
    profile_name="bedrock-lab",
    region_name="us-east-1",
)

model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    boto_session=aws_session,
    max_tokens=256,
    streaming=False,
)

session_manager = SnapshotSessionManager(
    session_id="customer-session-003",
    storage=LocalFileStorage("./sessions"),
)

skills_plugin = AgentSkills(skills=["./skills"])

agent = Agent(
    model=model,
    tools=[lookup_customer, get_order_history, process_refund],
    hooks=[ToolCallLimiter(max_calls=3)],
    plugins=[skills_plugin, RefundWorkflowHandler()],
    session_manager=session_manager,
    system_prompt=(
    "You are a customer support assistant for a fictional electronics store. "
    "Answer only what the customer asks. "
    "Use conversation history to recall details they provided. "
    "When given a support reference, acknowledge it; it is not an order ID. "
    "Only start a refund workflow when the customer explicitly requests one. "
    "For refund requests, activate the refund-processing skill and follow it. "
    "Use tools when customer or order records are needed. "
    "Refunds are simulations with no payments or balance changes. "
    "Provide a short final answer without reasoning narration or thinking tags."
    ),
    callback_handler=None,
)

if __name__ == "__main__":
    print("Session:", session_manager.session_id)
    print("Restored messages:", len(agent.messages))
    print("Type /exit to leave.")

    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if prompt.lower() == "/exit":
            break

        if not prompt:
            continue

        response = agent(prompt)
        answer = re.sub(
            r"<thinking>.*?(?:</thinking>|$)",
            "",
            str(response),
            flags=re.DOTALL | re.IGNORECASE,
        ).strip()
        print("Agent:", answer or "No final answer was returned.")
        print("Stop reason:", response.stop_reason)