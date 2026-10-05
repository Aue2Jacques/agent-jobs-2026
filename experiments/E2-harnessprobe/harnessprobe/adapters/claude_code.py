import json
import os
from .base import Adapter, Outcome


class ClaudeCode(Adapter):
    name = "cc"
    protocol = "anthropic"
    ua_hint = "claude-cli"
    tools = {"run_command": ("Bash", "command")}

    def command(self, prompt, base_url, home):
        return [os.environ.get("HP_CLAUDE_BIN", "claude"), "-p", prompt, "--model", "claude-sonnet-5",
                "--output-format", "json", "--dangerously-skip-permissions"]

    def env(self, base_url, home):
        return {"CLAUDE_CONFIG_DIR": home, "ANTHROPIC_BASE_URL": base_url, "ANTHROPIC_API_KEY": "sk-ant-test",
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1", "IS_SANDBOX": "1"}

    def parse(self, stdout, stderr, exit_code):
        try:
            d = json.loads(stdout)
        except ValueError:
            return Outcome(exit_code, error=(stderr or stdout)[-500:], is_error=True)
        res = d.get("result") or ""
        err = res if d.get("is_error") else ""
        return Outcome(exit_code, final_text="" if d.get("is_error") else res, is_error=bool(d.get("is_error")),
                       error=err, raw_events=d.get("num_turns") or 0)
