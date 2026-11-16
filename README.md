# json-log-inspector

Summarize JSON Lines application logs with level counts, latency percentiles and top errors.

A small, dependency-free Python project designed to be useful on its own and easy
for coding agents to understand. Runs locally; no API keys or services required.

## Quick start

Requires Python 3.11 or newer. From the repository root:

```sh
python -m log_inspector examples/app.jsonl
python -m unittest discover -s tests -v
```

Optional installation in a virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
json-log-inspector --help
```

## Behavior and limits

Each nonblank line must be a JSON object. `level` is a string (default UNKNOWN);
`message` groups ERROR/CRITICAL events. Optional `duration_ms` must be a finite,
nonnegative number; booleans are rejected. Percentiles use nearest rank, without
interpolation. Invalid records are reported by line number and skipped; invalid
durations do not discard otherwise valid records. Latencies are kept in memory
for exact percentiles. Top errors sort by count, then message, limited to five.
Exit codes: 0 clean input, 1 malformed records/durations, 2 I/O or encoding error.

## Layout

- `log_inspector/core.py`: public functions and command-line interface.
- `tests/`: unit and command-line regression tests.
- `examples/`: small, synthetic inputs safe to share publicly.
- `AGENTS.md`: orientation and working conventions for coding agents.
- `docs/architecture.md`: data flow and extension points.

## Possible next steps

- Add time-window filtering.
- Add per-service summaries.
- Add bounded-memory approximate percentiles.

These are suggestions for future work, not implemented features.

## Development

Tests use the Python standard library. The CI workflow runs them on Python 3.11
and 3.12. Keep changes focused and add regression tests for behavior changes.
The project is intentionally small; it does not claim production readiness.

## License

MIT. See [LICENSE](LICENSE).
