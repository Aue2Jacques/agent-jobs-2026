import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request

from .adapters import ADAPTERS
from .scenarios import all_fixtures, build

AIMOCK_PORT, RAW_PORT = 4010, 4011
HERE = os.path.dirname(os.path.abspath(__file__))


def _alive(port):
    try:
        urllib.request.urlopen("http://127.0.0.1:%d/health" % port, timeout=2)
        return True
    except Exception as e:  # rawsse answers 404 on GET, which still means alive
        return getattr(e, "code", None) == 404


def start_mocks(out):
    """(Re)start aimock with generated fixtures and the raw SSE fault server. Returns the processes."""
    fx = os.path.join(out, "fixtures")
    os.makedirs(fx, exist_ok=True)
    with open(os.path.join(fx, "generated.json"), "w") as f:
        json.dump(all_fixtures(ADAPTERS.values()), f, indent=1)
    procs = []
    aimock = os.environ.get("HP_AIMOCK_BIN", "llmock")
    procs.append(subprocess.Popen([aimock, "-p", str(AIMOCK_PORT), "-f", fx, "--log-level", "warn", "--journal-max", "0"],
                                  stdout=open(os.path.join(out, "aimock.log"), "w"), stderr=subprocess.STDOUT,
                                  start_new_session=True))
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "mock", "rawsse.py"), str(RAW_PORT),
                                   os.path.join(out, "rawsse.log")],
                                  stdout=open(os.path.join(out, "rawsse.out"), "w"), stderr=subprocess.STDOUT,
                                  start_new_session=True))
    for port in (AIMOCK_PORT, RAW_PORT):
        for _ in range(30):
            if _alive(port):
                break
            time.sleep(0.5)
    return procs


def stop_mocks(procs):
    for p in procs:
        try:
            os.killpg(p.pid, signal.SIGTERM)
        except Exception:
            pass


def count_requests(out, adapter, scen, t0, t1):
    n = 0
    if scen["mock"] == "aimock":
        try:
            journal = json.load(urllib.request.urlopen("http://127.0.0.1:%d/__aimock/journal?limit=100000" % AIMOCK_PORT, timeout=10))
        except Exception:
            return -1
        for e in journal:
            ua = (e.get("headers") or {}).get("user-agent", "").lower()
            match = (((e.get("response") or {}).get("fixture") or {}).get("match") or {}).get("userMessage") or ""
            body = e.get("body") or {}
            agent_loop = body.get("__aimock_truncated") or bool(body.get("tools"))   # skip side requests such as title generation
            if adapter.ua_hint in ua and agent_loop and t0 * 1000 <= e["timestamp"] <= t1 * 1000 + 1000 and scen["marker"].startswith(match or "\0"):
                n += 1
    else:
        with open(os.path.join(out, "rawsse.log")) as f:
            for line in f:
                r = json.loads(line)
                if adapter.ua_hint in r["ua"].lower() and r.get("tools", True) and r["scenario"] == scen["marker"] and t0 <= r["t"] <= t1 + 1:
                    n += 1
    return n


def run_one(out, adapter, name, scen):
    d = os.path.join(out, "runs", "%s_%s" % (adapter.name, name))
    shutil.rmtree(d, ignore_errors=True)
    work, home = os.path.join(d, "work"), os.path.join(d, "home")
    os.makedirs(work)
    port = AIMOCK_PORT if scen["mock"] == "aimock" else RAW_PORT
    base_url = "http://127.0.0.1:%d" % port
    adapter.setup(base_url, home)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("ANTHROPIC_", "OPENAI_", "CLAUDE"))}
    env.update(adapter.env(base_url, home))
    env["PWD"] = work          # some harnesses (OpenCode) trust $PWD over the real cwd
    prompt = "%s please handle this request (%s)." % (scen["marker"], adapter.name)
    t0 = time.time()
    p = subprocess.Popen(adapter.command(prompt, base_url, home), cwd=work, env=env, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        so, se = p.communicate(timeout=scen["timeout"])
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(p.pid, signal.SIGKILL)
        so, se = p.communicate()
    t1 = time.time()
    so, se = so.decode("utf-8", "replace"), se.decode("utf-8", "replace")
    with open(os.path.join(d, "stdout.txt"), "w") as f:
        f.write(so[-200000:])
    with open(os.path.join(d, "stderr.txt"), "w") as f:
        f.write(se[-50000:])
    o = adapter.parse(so, se, p.returncode)
    o.timed_out = timed_out
    ctx = {"workdir": work, "requests": count_requests(out, adapter, scen, t0, t1), "full_text": scen.get("full_text")}
    verdict = scen["verdict"](o, ctx)
    row = dict(harness=adapter.name, scenario=name, verdict=verdict, seconds=round(t1 - t0, 1), requests=ctx["requests"],
               files=sorted(os.listdir(work)), outcome=o.to_dict(), note=scen.get("note", ""))
    with open(os.path.join(d, "result.json"), "w") as f:
        json.dump(row, f, ensure_ascii=False, indent=1)
    return row


def run(harnesses, scenarios, out):
    os.makedirs(out, exist_ok=True)
    procs = start_mocks(out)
    results, lock = [], threading.Lock()

    def worker(h):
        a = ADAPTERS[h]
        S = build(a)
        for name in scenarios:
            if name not in S:
                continue
            row = run_one(out, a, name, S[name])
            with lock:
                results.append(row)
                with open(os.path.join(out, "results.jsonl"), "a") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                print("%s %-6s %-14s %-14s %6.1fs req=%s" % (time.strftime("%H:%M:%S"), h, name, row["verdict"],
                                                         row["seconds"], row["requests"]), flush=True)

    threads = [threading.Thread(target=worker, args=(h,)) for h in harnesses]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stop_mocks(procs)
    return results
