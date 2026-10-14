#!/usr/bin/env python3
"""Non-destructive MCP stdio smoke test for viRustGIS.

Usage: python scripts/mcp_smoke.py --exe target/release/rustgis-cli
"""
import argparse
import json
import subprocess
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--exe", default="target/release/rustgis-cli")
    p.add_argument("--timeout", type=float, default=30)
    args = p.parse_args()
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18",
                    "capabilities": {}, "clientInfo": {"name": "virustgis-smoke", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "list_layers", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 4, "method": "ping", "params": {}},
    ]
    payload = "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in messages)
    try:
        completed = subprocess.run(
            [args.exe, "mcp", "--sample", "--no-plugins"],
            input=payload, text=True, capture_output=True,
            timeout=args.timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"Failed to execute MCP server: {exc}", file=sys.stderr)
        return 1
    if completed.returncode != 0:
        print(completed.stderr[-2000:], file=sys.stderr)
        return 1
    try:
        replies = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    except json.JSONDecodeError as exc:
        print(f"stdout is not JSON-RPC: {exc}", file=sys.stderr)
        return 1
    by_id = {v.get("id"): v for v in replies if isinstance(v, dict)}
    if set(by_id) != {1, 2, 3, 4}:
        print(f"Unexpected MCP response IDs: {list(by_id)}", file=sys.stderr)
        return 1
    for n in (1, 2, 3, 4):
        if "error" in by_id[n] or "result" not in by_id[n]:
            print(f"MCP request {n} failed: {by_id[n]}", file=sys.stderr)
            return 1
    names = {t["name"] for t in by_id[2]["result"].get("tools", [])}
    required = {"list_layers", "search_commands", "run_command",
                "search_tools", "describe_tool", "run_tool", "view_map"}
    if not required.issubset(names):
        print(f"Missing tools: {required - names}", file=sys.stderr)
        return 1
    if by_id[3]["result"].get("isError"):
        print(f"list_layers failed: {by_id[3]}", file=sys.stderr)
        return 1
    print(f"OK: initialize, tools/list ({len(names)} tools), list_layers, ping")
    return 0


if __name__ == "__main__":
    sys.exit(main())
