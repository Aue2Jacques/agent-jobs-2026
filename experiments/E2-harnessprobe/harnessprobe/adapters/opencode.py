import json
import os
from .base import Adapter, Outcome, json_lines


class OpenCode(Adapter):
    name = "oc"
    protocol = "chat"
    ua_hint = "opencode"
    tools = {"run_command": ("bash", "command")}

    def setup(self, base_url, home):
        for sub in ("data", "config", "state"):
            os.makedirs(os.path.join(home, sub), exist_ok=True)
        cfg = {"$schema": "https://opencode.ai/config.json",
               "provider": {"mock": {"npm": "@ai-sdk/openai-compatible", "name": "Mock",
                                     "options": {"baseURL": base_url + "/v1", "apiKey": "x"},
                                     "models": {"mock-model": {"name": "mock-model"}}}},
               "model": "mock/mock-model", "autoupdate": False, "share": "disabled"}
        with open(os.path.join(home, "opencode.json"), "w") as f:
            json.dump(cfg, f)

    def command(self, prompt, base_url, home):
        return [os.environ.get("HP_OPENCODE_BIN", "opencode"), "run", "--model", "mock/mock-model", "--format", "json", prompt]

    def env(self, base_url, home):
        return {"OPENCODE_CONFIG": os.path.join(home, "opencode.json"), "XDG_DATA_HOME": os.path.join(home, "data"),
                "XDG_CONFIG_HOME": os.path.join(home, "config"), "XDG_STATE_HOME": os.path.join(home, "state"),
                "XDG_CACHE_HOME": os.environ.get("HP_OPENCODE_CACHE", os.path.join(home, "cache")),
                "OPENCODE_DISABLE_AUTOUPDATE": "1"}

    def parse(self, stdout, stderr, exit_code):
        texts, errors, tools, finishes, n = [], [], [], [], 0
        for ev in json_lines(stdout):
            n += 1
            t, p = ev.get("type"), ev.get("part") or {}
            if t == "text":
                texts.append(p.get("text", ""))
            elif t == "tool_use":
                st = p.get("state") or {}
                tools.append({"tool": p.get("tool"), "status": st.get("status"), "input": st.get("input")})
            elif t == "step_finish":
                finishes.append(p.get("reason"))
            elif t == "error":
                errors.append(json.dumps(ev.get("error") or ev)[:300])
        return Outcome(exit_code, final_text=texts[-1] if texts else "", is_error=bool(errors) or exit_code != 0,
                       error=" | ".join(errors)[-1000:], tool_events=tools + [{"finish": f} for f in finishes[-3:]],
                       raw_events=n)
