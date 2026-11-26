#!/usr/bin/env python3
"""Measure OpenCode efficiency: turns, step time, tool share, reasoning share.

Reads the current session_v2/session_message/session_part schema by default.
Use --legacy for the older session/message/part schema.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from collections import Counter, defaultdict


def pctl(values, p):
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, int(len(values) * p) - 1))
    return values[idx]


def load_json(raw):
    try:
        return json.loads(raw)
    except Exception:
        return None


def tool_duration(d):
    tt = d.get("time") or {}
    if not tt.get("completed"):
        tt = (d.get("state") or {}).get("time") or {}
    start = tt.get("ran") or tt.get("start") or tt.get("created")
    end = tt.get("completed") or tt.get("end")
    if start and end:
        return (end - start) / 1000
    return 0.0


def msg_duration(d):
    tt = d.get("time") or {}
    if tt.get("created") and tt.get("completed"):
        return (tt["completed"] - tt["created"]) / 1000
    if tt.get("start") and tt.get("end"):
        return (tt["end"] - tt["start"]) / 1000
    return 0.0


def classify_tool(name):
    if name in ("shell", "bash"):
        return "bash"
    if name in ("task", "subagent", "delegate"):
        return "task"
    return name or "?"


def iter_requests_v2(cur, sid):
    msgs = cur.execute(
        "select id, type, data from session_message where session_id = ? order by seq",
        (sid,),
    ).fetchall()
    parts_by_msg = defaultdict(list)
    for mid, raw in cur.execute(
        "select message_id, data from session_part where session_id = ?", (sid,)
    ):
        d = load_json(raw)
        if d:
            parts_by_msg[mid].append(d)

    current_user = None
    assistants = []
    for mid, mtype, raw in msgs:
        d = load_json(raw)
        if not d:
            continue
        if mtype == "user":
            if current_user is not None:
                yield current_user, assistants, parts_by_msg
            current_user = d
            assistants = []
        elif mtype == "assistant":
            assistants.append((mid, d))
    if current_user is not None:
        yield current_user, assistants, parts_by_msg


def iter_requests_legacy(cur, sid):
    msgs = cur.execute(
        "select id, data from message where session_id = ?", (sid,)
    ).fetchall()
    users = {}
    assistants = defaultdict(list)
    for mid, raw in msgs:
        d = load_json(raw)
        if not d:
            continue
        if d.get("role") == "user":
            users[mid] = d
        elif d.get("role") == "assistant":
            assistants[d.get("parentID")].append((mid, d))

    parts_by_msg = defaultdict(list)
    for mid, raw in cur.execute(
        "select message_id, data from part where session_id = ?", (sid,)
    ):
        d = load_json(raw)
        if d:
            parts_by_msg[mid].append(d)

    for uid in users:
        yield users[uid], assistants.get(uid, []), parts_by_msg


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    default_db = os.path.expanduser("~/.local/share/opencode/opencode.db")
    ap = argparse.ArgumentParser(
        description="Report turns, step time, tool share, and reasoning share per request."
    )
    ap.add_argument("--db", default=default_db, help="Path to opencode.db")
    ap.add_argument("--days", type=int, default=14, help="Only sessions from the last N days")
    ap.add_argument("--all", action="store_true", help="Ignore the day window")
    ap.add_argument("--legacy", action="store_true", help="Use the old session/message/part schema")
    ap.add_argument("--limit", type=int, default=10, help="Top requests to show")
    ap.add_argument("--out", help="Write the report to this UTF-8 file")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"DB not found: {args.db}")

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA query_only = ON")
    cur = con.cursor()

    cutoff = 0 if args.all else int((time.time() - args.days * 86400) * 1000)
    if args.legacy:
        sessions = cur.execute(
            "select id, title from session where parent_id is null and time_created >= ?",
            (cutoff,),
        ).fetchall()
        iter_requests = iter_requests_legacy
        source = "legacy"
    else:
        sessions = cur.execute(
            "select id, title from session_v2 where parent_id is null and time_created >= ?",
            (cutoff,),
        ).fetchall()
        iter_requests = iter_requests_v2
        source = "v2"

    requests = []
    tool_time = Counter()
    tool_calls = Counter()
    total_step = total_tool = total_reason = 0.0

    for sid, title in sessions:
        for _user, assistants, parts_by_msg in iter_requests(cur, sid):
            if not assistants:
                continue
            step = reason = tool = 0.0
            bash = task = calls = 0
            for mid, d in assistants:
                step += msg_duration(d)
                for p in parts_by_msg.get(mid, []):
                    ptype = p.get("type")
                    if ptype == "reasoning":
                        reason += msg_duration(p)
                    elif ptype == "tool":
                        calls += 1
                        name = classify_tool(p.get("name") or p.get("tool"))
                        tool_calls[name] += 1
                        dur = tool_duration(p)
                        tool += dur
                        tool_time[name] += dur
                        if name == "bash":
                            bash += 1
                        elif name == "task":
                            task += 1
            if step <= 0:
                continue
            requests.append(
                {
                    "title": title,
                    "turns": len(assistants),
                    "step": step,
                    "tool": tool,
                    "reason": reason,
                    "calls": calls,
                    "bash": bash,
                    "task": task,
                }
            )
            total_step += step
            total_tool += tool
            total_reason += reason

    if not requests:
        if args.all:
            sys.exit(f"No requests found in the {source} schema.")
        sys.exit(
            f"No requests found in the last {args.days} days ({source} schema). "
            "Try --all or a larger --days value."
        )

    turns = [r["turns"] for r in requests]
    steps = [r["step"] for r in requests]
    calls = [r["calls"] for r in requests]

    out = open(args.out, "w", encoding="utf-8") if args.out else None

    def emit(*a, **k):
        print(*a, **k, file=out or sys.stdout)

    emit(f"Lean Run - baseline ({source})")
    emit(f"DB: {args.db}")
    emit(f"Window: {'all time' if args.all else f'last {args.days} days'}")
    emit(f"Sessions: {len(sessions)} | Requests: {len(requests)}\n")

    emit(f"Turns/request      median {pctl(turns, .5):.0f}   p90 {pctl(turns, .9):.0f}")
    emit(f"Step min/request   median {pctl(steps, .5)/60:.1f}   p90 {pctl(steps, .9)/60:.1f}")
    emit(f"Tool calls/request median {pctl(calls, .5):.0f}   p90 {pctl(calls, .9):.0f}")
    if total_step:
        emit(f"Tool share of step {100*total_tool/total_step:.0f}%")
        emit(f"Reasoning share    {100*total_reason/total_step:.0f}%")
    emit()

    emit("Tool time (top):")
    for name, sec in tool_time.most_common(8):
        emit(f"  {name:10} {sec/3600:6.1f}h  calls={tool_calls[name]}")
    emit()

    emit(f"Top requests by step time (limit {args.limit}):")
    for r in sorted(requests, key=lambda x: -x["step"])[: args.limit]:
        emit(
            f"  {r['step']/60:7.1f}m  turns={r['turns']:4}  "
            f"bash={r['bash']:3}  task={r['task']:2}  {r['title'][:48]}"
        )
    if out:
        out.close()


if __name__ == "__main__":
    main()
