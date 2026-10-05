import argparse
import json
import os

from .adapters import ADAPTERS
from .scenarios import build


def main():
    ap = argparse.ArgumentParser(prog="harnessprobe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run scenarios against harnesses")
    r.add_argument("--harness", default=",".join(ADAPTERS), help="comma list: " + ",".join(ADAPTERS))
    r.add_argument("--scenarios", default="all")
    r.add_argument("--out", default="out")
    sub.add_parser("list", help="list scenarios per harness")
    s = sub.add_parser("summary", help="print a harness x scenario verdict table")
    s.add_argument("--out", default="out")
    a = ap.parse_args()
    if a.cmd == "list":
        for h, ad in ADAPTERS.items():
            print(h, ad.protocol, " ".join(sorted(build(ad))))
    elif a.cmd == "run":
        from .runner import run
        hs = a.harness.split(",")
        names = sorted({n for h in hs for n in build(ADAPTERS[h])}) if a.scenarios == "all" else a.scenarios.split(",")
        run(hs, names, os.path.abspath(a.out))
    elif a.cmd == "summary":
        rows = [json.loads(l) for l in open(os.path.join(a.out, "results.jsonl"))]
        hs = sorted({r["harness"] for r in rows})
        names = sorted({r["scenario"] for r in rows})
        cell = {(r["harness"], r["scenario"]): r for r in rows}
        print("%-15s" % "scenario" + "".join("%-22s" % h for h in hs))
        for n in names:
            line = "%-15s" % n
            for h in hs:
                r = cell.get((h, n))
                line += "%-22s" % ("%s (%d req)" % (r["verdict"], r["requests"]) if r else "-")
            print(line)


main()
