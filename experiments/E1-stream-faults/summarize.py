import json,os,re,glob
E="/workspace/harness-faults"
def final(h,txt):
    if h=="cc":
        try:
            d=json.loads(txt); return f"subtype={d.get('subtype')} is_error={d.get('is_error')} turns={d.get('num_turns')} result={str(d.get('result'))[:160]!r}"
        except Exception: return "non-json: "+txt[-200:]
    lines=[json.loads(l) for l in txt.splitlines() if l.strip().startswith("{")]
    out=[]
    for l in lines:
        t=l.get("type")
        if h=="codex":
            it=l.get("item") or {}
            if t=="item.completed" and it.get("type")=="agent_message": out.append(f"msg={it.get('text','')[:120]!r}")
            elif t=="item.completed" and it.get("type")=="error" and "metadata" not in it.get("message",""): out.append(f"ERR={it.get('message','')[:160]!r}")
            elif t=="item.completed" and it.get("type")=="command_execution": out.append(f"cmd={it.get('command','')[:80]!r} exit={it.get('exit_code')}")
            elif t in("turn.failed","error"): out.append(f"{t}={json.dumps(l)[:200]}")
            elif t=="turn.completed": out.append("turn.completed")
        else:
            p=l.get("part") or {}
            if t=="text": out.append(f"text={p.get('text','')[:120]!r}")
            elif t=="tool_use": out.append(f"tool={p.get('tool')} status={(p.get('state') or {}).get('status')} in={json.dumps((p.get('state') or {}).get('input'))[:80]}")
            elif t=="step_finish": out.append(f"finish={p.get('reason')}")
            elif t=="error": out.append(f"ERROR={json.dumps(l.get('error') or l)[:200]}")
    return " | ".join(out) if out else "(no events)"
for h in ["cc","codex","oc"]:
    for c in ["RAW_NOFINISH","RAW_INCOMPLETE","RAW_BODYSTALL","RAW_KEEPALIVE","OK","EMPTY","LEN0","CUT","FLAKY","TOOLOK","TRUNCTOOL","TOOLCUT","STALL"]:
        n=(f"raw_{h}_{c[4:]}" if c.startswith("RAW") else f"{h}_{c}"); m=f"{E}/out/{n}.meta"
        if not os.path.exists(m): continue
        meta=open(m).read().split("\n")
        files=[x for x in meta[1:] if x]
        err=open(f"{E}/out/{n}.err").read().strip().splitlines()
        err=[e for e in err if "Reading additional input" not in e]
        print(f"[{n}] {meta[0]} files={files}")
        print("   ", final(h,open(f"{E}/out/{n}.out").read()))
        if err: print("    stderr:", " / ".join(err[-3:])[:300])
