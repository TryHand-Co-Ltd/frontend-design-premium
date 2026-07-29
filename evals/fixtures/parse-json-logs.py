#!/usr/bin/env python3
"""Fixture for eval #20 — non-UI backend task.

The agent should write/finish a Python log parser only.
Do NOT activate frontend-design or frontend-design-premium,
create DESIGN.md/UX-CONTRACT.md, or apply UI production contracts.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return events


def summarize(events: list[dict[str, Any]]) -> list[tuple[str, int, int, float]]:
    totals: dict[str, int] = defaultdict(int)
    errors: dict[str, int] = defaultdict(int)
    for event in events:
        service = str(event.get("service") or "unknown")
        totals[service] += 1
        level = str(event.get("level") or "").lower()
        if level in {"error", "fatal", "critical"}:
            errors[service] += 1
    rows: list[tuple[str, int, int, float]] = []
    for service in sorted(totals):
        total = totals[service]
        err = errors[service]
        rate = (err / total * 100.0) if total else 0.0
        rows.append((service, total, err, rate))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize error rates by service from JSONL logs.")
    parser.add_argument("logfile", type=Path, help="Path to JSONL log file")
    args = parser.parse_args()
    rows = summarize(load_events(args.logfile))
    print(f"{'service':<24} {'events':>8} {'errors':>8} {'error%':>8}")
    print("-" * 52)
    for service, total, err, rate in rows:
        print(f"{service:<24} {total:>8} {err:>8} {rate:>7.2f}%")


if __name__ == "__main__":
    main()
