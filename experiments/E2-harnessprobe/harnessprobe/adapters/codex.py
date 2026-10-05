import os
from .base import Adapter, Outcome, json_lines

CONFIG = """model = "mock-model"
model_provider = "mock"
[model_providers.mock]
name = "mock"
base_url = "{base_url}/v1"
env_key = "MOCK_API_KEY"
wire_api = "responses"
"""


class Codex(Adapter):
    name = "codex"
    protocol = "responses"
    ua_hint = "codex"
    tools = {"run_command": ("exec_command", "cmd")}

    def setup(self, base_url, home):
        os.makedirs(home, exist_ok=True)
        with open(os.path.join(home, "config.toml"), "w") as f:
            f.write(CONFIG.format(base_url=base_url))

    def command(self, prompt, base_url, home):
        return [os.environ.get("HP_CODEX_BIN", "codex"), "exec", "--skip-git-repo-check", "--json",
                "--dangerously-bypass-approvals-and-sandbox", prompt]

    def env(self, base_url, home):
        return {"CODEX_HOME": home, "MOCK_API_KEY": "x"}

    def parse(self, stdout, stderr, exit_code):
        texts, errors, tools, n = [], [], [], 0
        for ev in json_lines(stdout):
            n += 1
            t, item = ev.get("type"), ev.get("item") or {}
            if t == "item.completed" and item.get("type") == "agent_message":
                texts.append(item.get("text", ""))
            elif t == "item.completed" and item.get("type") == "command_execution":
                tools.append({"cmd": item.get("command"), "exit": item.get("exit_code")})
            elif t == "item.completed" and item.get("type") == "error" and "metadata" not in item.get("message", ""):
                errors.append(item.get("message", ""))
            elif t in ("turn.failed", "error"):
                errors.append((ev.get("error") or {}).get("message") or ev.get("message", ""))
        failed = any(e for e in errors if not e.startswith("Reconnecting"))
        return Outcome(exit_code, final_text=texts[-1] if texts else "", is_error=failed or exit_code != 0,
                       error=" | ".join(errors)[-1000:], tool_events=tools, raw_events=n)
