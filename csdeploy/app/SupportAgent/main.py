import re
from pathlib import Path
from tempfile import gettempdir

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, AgentSkills
from strands.models import BedrockModel
from strands.session import SnapshotSessionManager
from strands.storage import LocalFileStorage

from customer_service_tools import (
    lookup_customer,
    get_order_history,
    process_refund,
)
from hooks import ToolCallLimiter
from steering_handlers import RefundWorkflowHandler

app = BedrockAgentCoreApp()

SKILLS_PATH = Path(__file__).resolve().parent / "skills"
storage = LocalFileStorage(
    str(Path(gettempdir()) / "customer-support-sessions")
)

SYSTEM_PROMPT = (
    "You are a customer support assistant for a fictional electronics store. "
    "Answer only what the customer asks. "
    "Use conversation history to recall details they provided. "
    "When given a support reference, acknowledge it; it is not an order ID. "
    "Only start a refund workflow when the customer explicitly requests one. "
    "For refund requests, activate the refund-processing skill and follow it. "
    "Use tools when customer or order records are needed. "
    "Refunds are simulations with no payments or balance changes. "
    "Provide a short final answer without reasoning narration or thinking tags."
)


@app.entrypoint
def invoke(payload, context):
    prompt = payload.get("prompt")

    if not isinstance(prompt, str) or not prompt.strip():
        return {"error": "Provide a non-empty prompt."}

    if not context.session_id:
        return {"error": "Provide a Runtime session ID."}

    skills_plugin = AgentSkills(skills=[str(SKILLS_PATH)])

    agent = Agent(
        model=BedrockModel(
            model_id="amazon.nova-pro-v1:0",
            region_name="us-east-1",
            max_tokens=256,
            streaming=False,
        ),
        tools=[lookup_customer, get_order_history, process_refund],
        hooks=[ToolCallLimiter(max_calls=3)],
        plugins=[skills_plugin, RefundWorkflowHandler()],
        session_manager=SnapshotSessionManager(
            session_id=context.session_id,
            storage=storage,
        ),
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
    )

    result = agent(prompt)

    answer = re.sub(
        r"<thinking>.*?(?:</thinking>|$)",
        "",
        str(result),
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()

    return {
        "reply": answer or "No final answer was returned.",
        "stop_reason": result.stop_reason,
        "session_id": context.session_id,
        "activated_skills": skills_plugin.get_activated_skills(agent),
    }


if __name__ == "__main__":
    app.run()