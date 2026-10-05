"""What every harness adapter must answer: how to launch it, which wire protocol it speaks,
how generic actions map onto its tools, and how to read its result."""
import json
from typing import Dict, List, Optional


class Outcome:
    def __init__(self, exit_code, final_text="", is_error=False, error="", tool_events=None, timed_out=False, raw_events=0):
        self.exit_code = exit_code
        self.final_text = final_text
        self.is_error = is_error
        self.error = error
        self.tool_events = tool_events or []
        self.timed_out = timed_out
        self.raw_events = raw_events

    def to_dict(self):
        return dict(exit_code=self.exit_code, final_text=self.final_text[:2000], is_error=self.is_error,
                    error=self.error[:1000], tool_events=self.tool_events[:50], timed_out=self.timed_out,
                    raw_events=self.raw_events)


class Adapter:
    name = "base"
    protocol = "chat"          # one of: anthropic, chat, responses
    tools = {}                 # generic action -> (tool name, argument key)

    def command(self, prompt: str, base_url: str, home: str) -> List[str]:
        raise NotImplementedError

    def env(self, base_url: str, home: str) -> Dict[str, str]:
        raise NotImplementedError

    def setup(self, base_url: str, home: str) -> None:
        """Write isolated config files under `home` (one fresh dir per run)."""

    def tool_call(self, action: str, **kw) -> Dict[str, str]:
        """Translate a generic action (run_command, ...) into this harness's tool name and JSON arguments."""
        if action == "run_command":
            name, key = self.tools["run_command"]
            return {"name": name, "arguments": json.dumps({key: kw["cmd"]})}
        raise KeyError(action)

    def parse(self, stdout: str, stderr: str, exit_code: int) -> Outcome:
        raise NotImplementedError


def json_lines(text: str):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                yield json.loads(line)
            except ValueError:
                pass
