#!/usr/bin/env python3
"""
03_trace_inspection.py — ECHO‑13 Trace Inspection
===================================================
Shows how to enable the built‑in execution tracer, capture every event the
engine emits, and produce human‑readable reports plus optional JSON export.

What this script does
---------------------
1. Enables tracing via ``EngineConfig(enable_tracing=True)``.
2. Builds a BRANCHING graph:  α → β, α → γ, β → δ
3. Runs the engine for a configurable number of passes (default 3).
4. Produces three reports:
   a) **Timeline** — every event, indented by recursion depth, with ⚡ on
      mutations.
   b) **Mutation summary** — per‑node mutation counts with a visual bar.
   c) **Per‑pass breakdown** — event and mutation counts for each pass.
5. Optionally dumps the raw trace as JSON (``--json`` flag).

Run
---
    # Default (3 passes, human‑readable output)
    python 03_trace_inspection.py

    # Custom passes + JSON dump
    python 03_trace_inspection.py --passes 5 --json
"""

from __future__ import annotations

import argparse
import json
import sys

from echo13.engine import EngineConfig, Session
from echo13.graph import Node, SymbolGraph


# ── Graph builder ───────────────────────────────────────────────────────
def build_branching_graph() -> SymbolGraph:
    """Return a branching graph:  α → β → δ,  α → γ"""
    graph = SymbolGraph()

    alpha = Node(label="α", value=1.0)
    beta = Node(label="β", value=2.0)
    gamma = Node(label="γ", value=3.0)
    delta = Node(label="δ", value=4.0)

    graph.add_node(alpha)
    graph.add_node(beta)
    graph.add_node(gamma)
    graph.add_node(delta)

    graph.add_edge(alpha, beta)
    graph.add_edge(alpha, gamma)
    graph.add_edge(beta, delta)

    return graph


# ── Report helpers ──────────────────────────────────────────────────────
def print_timeline(trace: list[dict]) -> None:
    """Print every trace event on one line, indented by recursion depth."""
    print("=" * 64)
    print("TIMELINE")
    print("=" * 64)

    for event in trace:
        depth = event.get("depth", 0)
        kind = event.get("kind", "?")
        node = event.get("node", "")
        value = event.get("value", "")
        mutated = event.get("mutated", False)
        pass_n = event.get("pass", "?")

        indent = "  " * depth
        flag = " ⚡" if mutated else ""
        print(f"  pass {pass_n}  {indent}{kind:<12} {node:<4} → {value}{flag}")

    print()


def print_mutation_summary(trace: list[dict]) -> None:
    """Print per‑node mutation counts with a simple bar chart."""
    print("=" * 64)
    print("MUTATION SUMMARY")
    print("=" * 64)

    counts: dict[str, int] = {}
    for event in trace:
        if event.get("mutated"):
            label = event.get("node", "?")
            counts[label] = counts.get(label, 0) + 1

    if not counts:
        print("  (no mutations recorded)")
    else:
        max_count = max(counts.values())
        bar_width = 30
        for label in sorted(counts):
            c = counts[label]
            bar_len = int(c / max_count * bar_width) if max_count else 0
            bar = "█" * bar_len
            print(f"  {label:<4} {bar:<{bar_width}} {c}")

    print()


def print_pass_breakdown(trace: list[dict], num_passes: int) -> None:
    """Print event and mutation counts for each pass."""
    print("=" * 64)
    print("PER‑PASS BREAKDOWN")
    print("=" * 64)
    print(f"  {'Pass':>6} {'Events':>8} {'Mutations':>10}")
    print("  " + "-" * 28)

    for p in range(1, num_passes + 1):
        events = [e for e in trace if e.get("pass") == p]
        mutations = sum(1 for e in events if e.get("mutated"))
        print(f"  {p:>6} {len(events):>8} {mutations:>10}")

    total_events = len(trace)
    total_mutations = sum(1 for e in trace if e.get("mutated"))
    print("  " + "-" * 28)
    print(f"  {'TOTAL':>6} {total_events:>8} {total_mutations:>10}")
    print()


# ── JSON export ─────────────────────────────────────────────────────────
def dump_json(trace: list[dict]) -> None:
    """Write the raw trace to stdout as pretty‑printed JSON."""
    print("=" * 64)
    print("RAW TRACE (JSON)")
    print("=" * 64)
    print(json.dumps(trace, indent=2, default=str))
    print()


# ── CLI ────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ECHO‑13 trace‑inspection demo",
    )
    parser.add_argument(
        "--passes", type=int, default=3,
        help="Number of recursive passes to execute (default: 3)",
    )
    parser.add_argument(
        "--json", action="store_true", dest="dump_json",
        help="Dump the raw trace as JSON after the reports",
    )
    return parser.parse_args()


# ── Main ───────────────────────────────────────────────────────────────
def main() -> None:
    args = parse_args()

    # 1. Config with tracing enabled
    config = EngineConfig(
        recursion_depth=3,
        mutation_rate=0.5,
        seed=42,
        enable_tracing=True,
    )

    # 2. Build graph
    graph = build_branching_graph()

    # 3. Run
    session = Session(config=config, graph=graph)
    for pass_number in range(1, args.passes + 1):
        session.run(pass_id=pass_number)

    # 4. Retrieve the trace
    trace: list[dict] = session.get_trace()

    if not trace:
        print("⚠  No trace events captured. Is enable_tracing set?")
        sys.exit(1)

    # 5. Reports
    print()
    print("ECHO‑13  ·  Trace Inspection")
    print(f"Passes executed: {args.passes}")
    print()

    print_timeline(trace)
    print_mutation_summary(trace)
    print_pass_breakdown(trace, args.passes)

    if args.dump_json:
        dump_json(trace)

    print("Trace inspection complete.")


if __name__ == "__main__":
    main()
