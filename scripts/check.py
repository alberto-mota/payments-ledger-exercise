#!/usr/bin/env python3
"""Compare your summary.json against fixtures/expected.json.

Usage: python3 scripts/check.py path/to/summary.json

Only the customers present in expected.json are compared. Your anomalies
list is not checked here; we'll look at it together.
"""
import json, sys, os

def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", "fixtures", "expected.json")) as f:
        expected = json.load(f)["customers"]
    with open(sys.argv[1]) as f:
        actual = json.load(f).get("customers", {})

    problems = 0
    for cid, exp in expected.items():
        act = actual.get(cid)
        if act is None:
            print(f"MISSING  {cid}"); problems += 1; continue
        for field, val in exp.items():
            if act.get(field) != val:
                print(f"MISMATCH {cid}.{field}: expected {val!r}, got {act.get(field)!r}")
                problems += 1
    if problems == 0:
        print(f"OK: {len(expected)} customers match")
    else:
        print(f"{problems} problem(s)")
        sys.exit(1)

if __name__ == "__main__":
    main()
