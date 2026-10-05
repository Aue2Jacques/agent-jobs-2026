"""Scenarios are written once, in terms of generic actions; adapters translate them per harness.
Each scenario: which mock serves it, the fixtures (for aimock), a time limit, and a verdict function."""
import json
import os

LONG = "PARTIAL_ANSWER: " + "the quick brown fox jumps over the lazy dog. " * 20


def _text(marker, content, **extra):
    f = {"match": {"userMessage": marker}, "response": {"content": content}}
    f.update(extra)
    return [f]


def _tool(marker, call, follow_up, **extra):
    """Model calls a tool once; after the tool result comes back it answers `follow_up`."""
    first = {"match": {"userMessage": marker}, "response": {"toolCalls": [call]}}
    first.update(extra)
    return [{"match": {"userMessage": marker, "hasToolResult": True}, "response": {"content": follow_up}}, first]


def reported(o):
    return o.exit_code != 0 or o.is_error


def v_fault(o, ctx):
    """For injected faults: the harness must either report the failure or fully recover."""
    if ctx["requests"] > 50:
        return "RETRY_STORM"
    if o.timed_out:
        return "HANG" if ctx["requests"] <= 1 else "SLOW_RETRY"
    if reported(o):
        return "PASS"
    full = ctx.get("full_text")
    if full and o.final_text.strip() == full.strip():
        return "PASS"          # recovered (e.g. fell back to a non-streaming request)
    return "FALSE_SUCCESS"


def v_tool_fault(marker_file, follow_up):
    """Tool call whose stream breaks mid-arguments: report the failure, or recover and run the *complete* command."""
    def f(o, ctx):
        base = v_fault(o, ctx)
        if base != "FALSE_SUCCESS":
            return base
        exists = os.path.exists(os.path.join(ctx["workdir"], marker_file))
        return "PASS" if (exists and follow_up in o.final_text) else "FALSE_SUCCESS"
    return f


def v_expect_text(text):
    def f(o, ctx):
        if o.timed_out:
            return "HANG"
        return "PASS" if (text in o.final_text and not reported(o)) else "FAIL"
    return f


def v_marker(should_exist, name):
    def f(o, ctx):
        exists = os.path.exists(os.path.join(ctx["workdir"], name))
        if o.timed_out:
            return "HANG"
        if exists and not should_exist:
            return "EXECUTED_INVALID"
        if should_exist and not exists:
            return "NOT_EXECUTED"
        return "PASS"
    return f


def build(adapter):
    h = adapter.name
    run = lambda cmd, cid: dict(adapter.tool_call("run_command", cmd=cmd), id=cid)
    bad = dict(adapter.tool_call("run_command", cmd="X"), id="call_tr_" + h)
    key = json.loads(bad["arguments"]).popitem()[0]
    bad["arguments"] = '{"%s": "echo TRUNC > marker_trunc.txt' % key        # unterminated JSON
    S = {}
    S["OK"] = dict(mock="aimock", fixtures=_text("CASE_OK", "BASELINE_OK all good."), timeout=300,
                   verdict=v_expect_text("BASELINE_OK"))
    S["EMPTY"] = dict(mock="aimock", fixtures=_text("CASE_EMPTY", ""), timeout=300, verdict=v_fault)
    S["LEN0"] = dict(mock="aimock", fixtures=[{"match": {"userMessage": "CASE_LEN0"},
                                               "response": {"content": "", "finishReason": "length"}}],
                     timeout=300, verdict=v_fault, note="aimock sends a non-standard event on the Responses protocol; use RAW_INCOMPLETE for codex")
    S["CUT"] = dict(mock="aimock", fixtures=_text("CASE_CUT", LONG, chunkSize=8, truncateAfterChunks=3, latency=50),
                    timeout=300, verdict=v_fault, full_text=LONG)
    S["FLAKY"] = dict(mock="aimock", fixtures=[
        {"match": {"userMessage": "CASE_FLAKY_" + h, "sequenceIndex": 0},
         "response": {"error": {"message": "upstream overloaded", "type": "server_error"}, "status": 500}},
        {"match": {"userMessage": "CASE_FLAKY_" + h}, "response": {"content": "FLAKY_RECOVERED"}}],
        timeout=300, verdict=v_expect_text("FLAKY_RECOVERED"), per_harness=True)
    S["TOOLOK"] = dict(mock="aimock", fixtures=_tool("CASE_TOOLOK_" + h, run("echo TOOL_OK > marker_ok.txt", "call_ok_" + h), "TOOL_DONE"),
                       timeout=300, verdict=v_marker(True, "marker_ok.txt"), per_harness=True)
    S["TRUNCTOOL"] = dict(mock="aimock", fixtures=_tool("CASE_TRUNCTOOL_" + h, bad, "AFTER_TRUNC"),
                          timeout=300, verdict=v_marker(False, "marker_trunc.txt"), per_harness=True)
    S["TOOLCUT"] = dict(mock="aimock", fixtures=_tool("CASE_TOOLCUT_" + h,
                        run("echo TOOLCUT_PARTIAL_COMMAND_THAT_IS_LONG > marker_toolcut.txt", "call_tc_" + h), "AFTER_TOOLCUT",
                        chunkSize=6, truncateAfterChunks=4, latency=50),
                        timeout=300, verdict=v_tool_fault("marker_toolcut.txt", "AFTER_TOOLCUT"), per_harness=True)
    S["STALL"] = dict(mock="aimock", fixtures=_text("CASE_STALL", "STALL_BEGIN and the rest arrives much later.", chunkSize=12, latency=900000),
                      timeout=720, verdict=v_fault)
    for raw in ("NOFINISH", "BODYSTALL", "KEEPALIVE", "INCOMPLETE"):
        S["RAW_" + raw] = dict(mock="raw", marker="RAW_" + raw, timeout=720 if raw in ("BODYSTALL", "KEEPALIVE") else 300,
                               verdict=v_fault)
    if adapter.protocol == "chat":
        S.pop("RAW_INCOMPLETE")
    if adapter.protocol == "responses":
        S.pop("LEN0")                    # aimock emits response.completed (status=incomplete) instead of response.incomplete          # rawsse.py does not implement finish_reason=length for chat completions yet
    for name, s in S.items():
        s.setdefault("marker", "CASE_" + name + ("_" + h if s.get("per_harness") else ""))
    return S


def all_fixtures(adapters):
    seen, out = set(), []
    for a in adapters:
        for s in build(a).values():
            for f in s.get("fixtures", []):
                k = json.dumps(f, sort_keys=True)
                if k not in seen:
                    seen.add(k)
                    out.append(f)
    # tool-result follow-ups must come before the first-turn fixture of the same marker
    out.sort(key=lambda f: 0 if f["match"].get("hasToolResult") else 1)
    return {"fixtures": out}
