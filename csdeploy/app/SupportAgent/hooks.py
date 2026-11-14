from strands.hooks import (
    HookProvider,
    HookRegistry,
    BeforeInvocationEvent,
    BeforeToolCallEvent,
)


class ToolCallLimiter(HookProvider):
    def __init__(self, max_calls: int = 3):
        self.max_calls = max_calls
        self.counts = {}

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.reset)
        registry.add_callback(BeforeToolCallEvent, self.check)

    def reset(self, event: BeforeInvocationEvent) -> None:
        self.counts = {}
        print("[HOOK] Tool counters reset")

    def check(self, event: BeforeToolCallEvent) -> None:
        name = event.tool_use["name"]
        self.counts[name] = self.counts.get(name, 0) + 1

        print(f"[HOOK] {name}: {self.counts[name]}/{self.max_calls}")

        if self.counts[name] > self.max_calls:
            event.cancel_tool = (
                f"Tool-call limit reached for {name}. "
                "Do not call this tool again during this request."
            )
            print(f"[HOOK] Blocked {name}")