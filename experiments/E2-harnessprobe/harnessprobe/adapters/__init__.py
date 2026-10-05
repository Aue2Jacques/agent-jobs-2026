from .claude_code import ClaudeCode
from .codex import Codex
from .opencode import OpenCode

ADAPTERS = {a.name: a for a in (ClaudeCode(), Codex(), OpenCode())}
