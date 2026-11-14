# Adapted from the AWS Strands workshop, Module 3.

from strands.vended_plugins.steering import (
    SteeringHandler,
    LedgerProvider,
    Proceed,
    Guide,
)


class RefundWorkflowHandler(SteeringHandler):
    name = "refund-workflow"

    def __init__(self):
        super().__init__(context_providers=[LedgerProvider()])

    async def steer_before_tool(self, *, agent, tool_use, **kwargs):
        if tool_use.get("name") != "process_refund":
            return Proceed(reason="Not a refund operation")

        customer_id = tool_use.get("input", {}).get("customer_id")
        ledger = self.steering_context.data.get("ledger") or {}
        calls = ledger.get("tool_calls", [])

        for required_tool in ("lookup_customer", "get_order_history"):
            completed = any(
                call.get("tool_name") == required_tool
                and call.get("status") == "success"
                and call.get("tool_args", {}).get("customer_id") == customer_id
                for call in calls
            )

            if not completed:
                print(f"[STEERING] Guiding agent: call {required_tool} first")
                return Guide(
                    reason=(
                        f"Call {required_tool} for customer {customer_id} "
                        "before retrying process_refund."
                    )
                )

        print("[STEERING] Prerequisite lookups found; allowing refund")
        return Proceed(reason="Required lookup steps completed")