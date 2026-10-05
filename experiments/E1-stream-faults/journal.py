import json,urllib.request,collections
d=json.load(urllib.request.urlopen("http://127.0.0.1:4010/__aimock/journal?limit=100000"))
rows=[]
for e in d:
    ua=e.get("headers",{}).get("user-agent","")
    h="cc" if "claude-cli" in ua else "codex" if "codex" in ua.lower() else "oc" if ("opencode" in ua.lower() or "ai-sdk" in ua.lower()) else ua[:30]
    r=e.get("response") or {}
    m=((r.get("fixture") or {}).get("match") or {})
    rows.append(dict(ts=e["timestamp"],h=h,path=e["path"],status=r.get("status"),match=m.get("userMessage"),toolres=m.get("hasToolResult"),interrupted=r.get("interrupted"),reason=r.get("interruptReason")))
json.dump(rows,open("/workspace/harness-faults/out/journal.json","w"),indent=1)
c=collections.Counter((x["h"],x["match"],x["toolres"],x["status"]) for x in rows)
for k,v in sorted(c.items(),key=str): print(v,k)
