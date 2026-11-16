"""Inspect local JSONL logs without sending data to an external service."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
from typing import Iterable

def percentile(values: list[float], percent: float) -> float | None:
    if not 0 < percent <= 100:
        raise ValueError("percent must be in (0, 100]")
    if not values:
        return None
    ordered = sorted(values)
    return ordered[math.ceil(len(ordered) * percent / 100) - 1]

def summarize(lines: Iterable[str]) -> dict:
    levels = Counter()
    errors = Counter()
    durations = []
    malformed = []
    invalid_durations = 0
    records = 0
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError("record must be an object")
            level = item.get("level", "UNKNOWN")
            if not isinstance(level, str):
                raise ValueError("level must be a string")
        except (ValueError, TypeError):
            malformed.append(number)
            continue
        records += 1
        level = level.upper()
        levels[level] += 1
        if level in {"ERROR", "CRITICAL"}:
            message = item.get("message", "(no message)")
            errors[message if isinstance(message, str) else "(non-string message)"] += 1
        if "duration_ms" in item:
            value = item["duration_ms"]
            try:
                valid = type(value) in (int, float) and value >= 0 and math.isfinite(value)
            except OverflowError:
                valid = False
            if valid:
                durations.append(value)
            else:
                invalid_durations += 1
    return {"records": records, "levels": dict(sorted(levels.items())),
            "malformed_lines": malformed, "invalid_durations": invalid_durations,
            "latency_ms": {"count": len(durations), "p50": percentile(durations, 50),
                           "p95": percentile(durations, 95)},
            "top_errors": [{"message": message, "count": count} for message, count in
                           sorted(errors.items(), key=lambda pair: (-pair[1], pair[0]))[:5]]}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        with args.path.open(encoding="utf-8") as stream:
            report = summarize(stream)
    except (OSError, UnicodeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return int(bool(report["malformed_lines"] or report["invalid_durations"]))
